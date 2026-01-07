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
    
    Returns:
        JSON: {
            'success': bool,
            'call_url': str,
            'pin': str,
            'did_number': str,
            'expires_in_minutes': int,
            'error': str (if failed)
        }
    """
    try:
        # Get QR code
        qr = get_object_or_404(
            PreGeneratedQR.objects.select_related('owner', 'gateway'),
            qr_code=qr_code.upper(),
            status='activated'
        )
        
        # Check if gateway is active
        if not qr.gateway or not qr.gateway.is_active:
            return JsonResponse({
                'success': False,
                'error': 'Gateway is not active'
            }, status=400)
        
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
