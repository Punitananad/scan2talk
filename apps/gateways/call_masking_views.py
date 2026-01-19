"""
Views for call masking functionality.
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from apps.gateways.qr_models import PreGeneratedQR
from apps.communications.call_masking_service import create_masked_call_for_qr
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/h', method='POST')
def generate_masked_call_url(request, qr_code):
    """
    Generate a masked call URL for contacting the QR code owner.
    
    Route: POST /gateways/call/<qr_code>/
    
    Handles payment logic:
    - If owner has balance >= ₹1: Deduct from owner, generate call
    - If owner has ₹0: Visitor must pay (handled by frontend redirect)
    
    Returns:
        JSON: {
            'success': bool,
            'call_url': str,
            'pin': str,
            'did_number': str,
            'expires_in_minutes': int,
            'payment_required': bool (if visitor must pay),
            'error': str (if failed)
        }
    """
    try:
        # Get QR code
        qr = get_object_or_404(
            PreGeneratedQR.objects.select_related('owner', 'gateway', 'category'),
            qr_code=qr_code.upper(),
            status='activated'
        )
        
        # Check if gateway is active
        if not qr.gateway or not qr.gateway.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Gateway is not active'
            }, status=400)
        
        # Check if prepaid category and handle payment
        if qr.category and qr.category.category_type == 'prepaid':
            try:
                from apps.accounts.recharge_models import QRWallet, QRWalletTransaction
                wallet = QRWallet.objects.get(qr_code=qr)
                
                # Check balance
                if wallet.balance >= 1.00:
                    # Owner has balance - deduct ₹1
                    wallet.balance -= 1.00
                    wallet.save()
                    
                    # Create transaction record
                    QRWalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='deduction',
                        amount=1.00,
                        description='Call charge',
                        notes=f'Masked call to {qr.owner.get_decrypted_phone()}'
                    )
                    
                    logger.info(f"✅ Deducted ₹1 from owner's wallet for call. New balance: ₹{wallet.balance}")
                    # Continue with call generation
                else:
                    # Owner has ₹0 - visitor must pay
                    logger.info(f"⚠️ Owner wallet empty. Visitor payment required for QR {qr_code}")
                    return JsonResponse({
                        'success': False,
                        'payment_required': True,
                        'cost': 1.00,
                        'error': 'Payment required. Owner wallet is empty.'
                    }, status=402)  # 402 Payment Required
            except QRWallet.DoesNotExist:
                # No wallet found, continue with call generation (free)
                logger.info(f"⚠️ No wallet found for QR {qr_code}, treating as free")
                pass
            except Exception as e:
                logger.error(f"Wallet check error for QR {qr_code}: {e}")
                # Continue with call generation if wallet check fails
                pass
        
        # Generate masked call
        result = create_masked_call_for_qr(qr)
        
        if result['success']:
            logger.info(f"Masked call generated for QR {qr_code}, PIN: {result['pin']}")
            return JsonResponse(result)
        else:
            logger.error(f"Failed to generate masked call for QR {qr_code}: {result.get('error')}")
            return JsonResponse(result, status=500)
            
    except Exception as e:
        logger.error(f"Error generating masked call for QR {qr_code}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@require_http_methods(["GET"])
def get_call_info(request, qr_code):
    """
    Get call masking information for a QR code (without generating new PIN).
    
    Route: GET /gateways/call/<qr_code>/info/
    
    Returns:
        JSON: {
            'success': bool,
            'did_number': str,
            'call_masking_enabled': bool
        }
    """
    try:
        qr = get_object_or_404(
            PreGeneratedQR.objects.select_related('gateway'),
            qr_code=qr_code.upper(),
            status='activated'
        )
        
        from django.conf import settings
        
        return JsonResponse({
            'success': True,
            'did_number': settings.SPARKTG_DID_NUMBER,
            'call_masking_enabled': bool(settings.SPARKTG_USERNAME and settings.SPARKTG_PASSWORD),
            'gateway_active': qr.gateway.is_active if qr.gateway else False
        })
        
    except Exception as e:
        logger.error(f"Error getting call info for QR {qr_code}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'QR code not found or not activated'
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='user', rate='5/h', method='POST')
def test_call_masking(request):
    """
    Test call masking feature for logged-in users.
    Uses user's own phone number for testing.
    
    Route: POST /gateways/test-call/
    
    Returns:
        JSON: {
            'success': bool,
            'call_url': str,
            'pin': str,
            'did_number': str,
            'expires_in_minutes': int
        }
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)
    
    try:
        from apps.communications.adapters.call_masking_adapter import CallMaskingAdapter
        
        # Get user's phone number
        user_phone = request.user.get_decrypted_phone() if hasattr(request.user, 'get_decrypted_phone') else None
        
        if not user_phone:
            return JsonResponse({
                'success': False,
                'error': 'No phone number found. Please update your profile.'
            }, status=400)
        
        # Generate test call
        adapter = CallMaskingAdapter()
        result = adapter.create_masked_call(
            owner_phone_number=user_phone,
            qr_id=f"TEST-{request.user.id}"
        )
        
        if result['success']:
            logger.info(f"Test call generated for user {request.user.email}, PIN: {result['pin']}")
            return JsonResponse(result)
        else:
            logger.error(f"Failed to generate test call for user {request.user.email}: {result.get('error')}")
            return JsonResponse(result, status=500)
            
    except Exception as e:
        logger.error(f"Error generating test call for user {request.user.email}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)
