"""
Wallet management views and APIs.
"""
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from uuid import uuid4
from .wallet_service import WalletService, RechargeGatewayService
from .wallet_models import Wallet, RechargeOrder
from .recharge_models import VisitorPayment

logger = logging.getLogger(__name__)


# Web Views
@login_required
def wallet_dashboard(request):
    """Wallet dashboard page."""
    wallet = WalletService.get_or_create_wallet(request.user)
    transactions = WalletService.get_transaction_history(request.user, limit=20)
    recent_orders = request.user.recharge_orders.all()[:10]
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/wallet_dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def recharge_wallet(request):
    """Recharge wallet page - Razorpay Payment Gateway."""
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            
            if amount < 1:
                messages.error(request, 'Minimum recharge amount is ₹1')
                return redirect('accounts:recharge_wallet')
            
            # Create recharge order
            order, payment_result = WalletService.create_recharge_order(
                user=request.user,
                amount=amount,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            if payment_result['success']:
                # Redirect to Razorpay checkout
                return redirect(payment_result['payment_url'])
            else:
                messages.error(request, f'Payment initiation failed: {payment_result.get("error")}')
                return redirect('accounts:recharge_wallet')
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('accounts:recharge_wallet')
    
    wallet = WalletService.get_or_create_wallet(request.user)
    context = {'wallet': wallet}
    return render(request, 'accounts/recharge_wallet.html', context)


@login_required
def recharge_success(request):
    """Recharge success page."""
    order_id = request.GET.get('order_id')
    context = {'order_id': order_id}
    return render(request, 'accounts/recharge_success.html', context)


@login_required
def recharge_cancel(request):
    """Recharge cancelled page."""
    messages.warning(request, 'Recharge cancelled')
    return redirect('accounts:wallet_dashboard')


# API Views
class WalletBalanceAPI(APIView):
    """API to get wallet balance."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            balance_info = WalletService.check_balance(request.user)
            return Response({
                'success': True,
                'data': balance_info
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class WalletTransactionsAPI(APIView):
    """API to get wallet transactions."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 50))
            transactions = WalletService.get_transaction_history(request.user, limit=limit)
            return Response({
                'success': True,
                'data': transactions
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class CreateRechargeOrderAPI(APIView):
    """API to create recharge order."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            amount = float(request.data.get('amount', 0))
            
            if amount < 1:
                return Response({
                    'success': False,
                    'error': 'Minimum recharge amount is ₹1'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            order = WalletService.create_recharge_order(
                user=request.user,
                amount=amount,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Initiate payment
            payment_result = RechargeGatewayService.initiate_recharge(order)
            
            if payment_result['success']:
                return Response({
                    'success': True,
                    'data': {
                        'order_id': order.order_id,
                        'amount': float(order.amount),
                        'credits': order.credits_to_add,
                        'payment_url': payment_result['payment_url'],
                        'gateway_order_id': payment_result['gateway_order_id']
                    }
                })
            else:
                return Response({
                    'success': False,
                    'error': payment_result.get('error')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def recharge_callback(request):
    """Handle payment gateway callback."""
    try:
        import json
        callback_data = json.loads(request.body)
        
        result = RechargeGatewayService.handle_callback(callback_data)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


class DeductCallCreditAPI(APIView):
    """API to deduct call credit (internal use)."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            qr_code = request.data.get('qr_code', '')
            notes = request.data.get('notes', 'Call initiated')
            
            result = WalletService.process_call_charge(
                user=request.user,
                qr_code=qr_code,
                notes=notes
            )
            
            return Response({
                'success': True,
                'data': result
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Test Payment Views (for development/testing)
@login_required
def test_payment_page(request, order_id):
    """Test payment page for development."""
    try:
        order = RechargeOrder.objects.get(order_id=order_id, user=request.user)
        context = {
            'order': order,
        }
        return render(request, 'accounts/test_payment.html', context)
    except RechargeOrder.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('accounts:wallet_dashboard')


@login_required
@require_http_methods(["POST"])
def test_payment_complete(request, order_id):
    """Complete test payment (for development)."""
    try:
        order = RechargeOrder.objects.get(order_id=order_id, user=request.user)
        
        # Simulate successful payment
        order.mark_completed(
            gateway_payment_id=f"TEST_PAY_{order_id}",
            gateway_signature="test_signature"
        )
        
        messages.success(request, f'Test payment successful! ₹{order.amount} credited to your wallet.')
        return redirect('accounts:recharge_success')
        
    except RechargeOrder.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('accounts:wallet_dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('accounts:wallet_dashboard')



# PhonePe Callback Handler
@csrf_exempt
@require_http_methods(["POST", "GET"])
def phonepe_callback(request):
    """Handle PhonePe payment callback."""
    try:
        from .phonepe_service import PhonePeGatewayService
        
        # Get callback data
        if request.method == 'POST':
            callback_data = request.POST.dict()
        else:
            callback_data = request.GET.dict()
        
        # Handle callback
        result = PhonePeGatewayService.handle_callback(callback_data)
        
        if result['success']:
            # Redirect to success page
            order_id = result.get('order_id', '')
            return redirect(f"/api/v1/auth/wallet/recharge/success/?order_id={order_id}")
        else:
            # Redirect to cancel page with error
            messages.error(request, result.get('message', 'Payment failed'))
            return redirect('accounts:recharge_cancel')
            
    except Exception as e:
        messages.error(request, f'Callback error: {str(e)}')
        return redirect('accounts:wallet_dashboard')


# Razorpay Integration
@csrf_exempt
@require_http_methods(["POST"])
def razorpay_webhook(request):
    """
    Handle Razorpay webhook callbacks.
    POST /api/v1/auth/wallet/recharge/callback/
    """
    try:
        from .razorpay_service import RazorpayGatewayService
        import json
        
        # Get raw body for signature verification
        raw_body = request.body
        signature = request.headers.get('X-Razorpay-Signature', '')
        
        # Verify webhook signature
        if not RazorpayGatewayService.verify_webhook_signature(raw_body, signature):
            logger.error("Razorpay webhook signature verification failed")
            return JsonResponse({
                'success': False,
                'message': 'Invalid signature'
            }, status=400)
        
        # Parse payload
        payload = json.loads(raw_body)
        
        # Handle webhook
        result = RazorpayGatewayService.handle_webhook(payload, signature)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"Razorpay webhook error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
def razorpay_checkout(request):
    """
    Razorpay checkout page.
    GET /api/v1/auth/wallet/razorpay/checkout/?order_id=<order_id>
    """
    try:
        from .razorpay_service import RazorpayGatewayService
        
        order_id = request.GET.get('order_id')
        if not order_id:
            messages.error(request, 'Order ID missing')
            return redirect('accounts:wallet_dashboard')
        
        order = RechargeOrder.objects.get(order_id=order_id, user=request.user)
        
        # Get Razorpay key
        service = RazorpayGatewayService()
        
        context = {
            'order': order,
            'razorpay_key_id': service.key_id,
            'razorpay_order_id': order.gateway_order_id,
            'amount': int(order.amount * 100),  # Amount in paise
            'currency': 'INR',
            'name': 'Scan2Talk',
            'description': f'Wallet Recharge - {order.credits_to_add} credits',
            'user_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email,
            'user_phone': request.user.get_decrypted_phone() if hasattr(request.user, 'get_decrypted_phone') else '',
        }
        
        return render(request, 'accounts/razorpay_checkout.html', context)
        
    except RechargeOrder.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('accounts:wallet_dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('accounts:wallet_dashboard')


@csrf_exempt
@require_http_methods(["POST"])
def razorpay_payment_success(request):
    """
    Handle Razorpay payment success callback from frontend.
    POST /api/v1/auth/wallet/razorpay/success/
    """
    try:
        from .razorpay_service import RazorpayGatewayService
        
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        # Verify signature
        if not RazorpayGatewayService.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        ):
            return JsonResponse({
                'success': False,
                'error': 'Invalid payment signature'
            }, status=400)
        
        # Find order
        order = RechargeOrder.objects.get(gateway_order_id=razorpay_order_id)
        
        # Mark as completed
        order.mark_completed(
            gateway_payment_id=razorpay_payment_id,
            gateway_signature=razorpay_signature
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment successful',
            'order_id': order.order_id,
            'redirect_url': f'/api/v1/auth/wallet/recharge/success/?order_id={order.order_id}'
        })
        
    except RechargeOrder.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Order not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



# Visitor Payment Views (for prepaid QR codes with ₹0 balance)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["POST"])
def initiate_visitor_payment(request, identifier):
    """
    Initiate visitor payment for contacting owner with ₹0 balance
    POST /api/v1/auth/wallet/visitor-pay/<identifier>/
    """
    try:
        from apps.gateways.qr_models import PreGeneratedQR
        from .phonepe_service import PhonePeGatewayService
        
        # Get QR code
        qr = get_object_or_404(
            PreGeneratedQR,
            qr_code=identifier.upper(),
            status='activated'
        )
        
        # Verify it's prepaid and owner has ₹0
        if not qr.category or qr.category.category_type != 'prepaid':
            return JsonResponse({
                'success': False,
                'error': 'This QR code does not require payment'
            })
        
        try:
            wallet = qr.qr_wallet
            if wallet.balance >= 1.00:
                return JsonResponse({
                    'success': False,
                    'error': 'Owner has balance. No payment required.'
                })
        except:
            return JsonResponse({
                'success': False,
                'error': 'Wallet not found'
            })
        
        # Get form data
        payment_type = request.POST.get('payment_type', 'message')  # 'message' or 'call'
        message_content = request.POST.get('message', '')
        intent = request.POST.get('intent', 'general')
        channel = request.POST.get('channel', 'sms')
        visitor_phone = request.POST.get('visitor_phone', '')
        
        # Create visitor payment record
        order_id = f"VP{uuid4().hex[:20].upper()}"
        
        visitor_payment = VisitorPayment.objects.create(
            qr_code=qr,
            amount=1.00,
            payment_type=payment_type,
            visitor_phone=visitor_phone,
            visitor_ip=get_client_ip(request),
            order_id=order_id,
            message_content=message_content,
            intent=intent,
            channel=channel,
            status='pending'
        )
        
        # Create a temporary order object for PhonePe
        class TempOrder:
            def __init__(self, visitor_payment):
                self.order_id = visitor_payment.order_id
                self.amount = visitor_payment.amount
                self.user = type('obj', (object,), {'id': 0})()  # Dummy user
                self.gateway_order_id = ''
                self.status = 'pending'
            
            def save(self):
                visitor_payment.gateway_order_id = self.gateway_order_id
                visitor_payment.save()
            
            def mark_failed(self, reason):
                visitor_payment.mark_failed(reason)
        
        temp_order = TempOrder(visitor_payment)
        result = PhonePeGatewayService.initiate_payment(temp_order)
        
        if result['success']:
            visitor_payment.gateway_order_id = result['transaction_id']
            visitor_payment.save()
            
            return JsonResponse({
                'success': True,
                'payment_url': result['payment_url'],
                'order_id': order_id
            })
        else:
            visitor_payment.mark_failed(result.get('error', 'Payment initiation failed'))
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Payment initiation failed')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST", "GET"])
def visitor_payment_callback(request):
    """
    Handle PhonePe callback for visitor payments
    POST/GET /api/v1/auth/wallet/visitor-pay/callback/
    """
    try:
        from .phonepe_service import PhonePeGatewayService
        
        # Get callback data
        if request.method == 'POST':
            callback_data = request.POST.dict()
        else:
            callback_data = request.GET.dict()
        
        # Handle callback
        result = PhonePeGatewayService.handle_callback(callback_data)
        
        if result['success']:
            # Find visitor payment by order_id
            order_id = result.get('order_id', '')
            
            # Check if it's a visitor payment (starts with VP)
            if order_id.startswith('VP'):
                try:
                    visitor_payment = VisitorPayment.objects.get(order_id=order_id)
                    visitor_payment.mark_completed(result.get('payment_id', ''))
                    
                    # Send the message/call now
                    send_visitor_communication(visitor_payment)
                    
                    # Redirect to success page
                    return redirect('accounts:visitor_payment_success', order_id=order_id)
                except VisitorPayment.DoesNotExist:
                    pass
        
        # Redirect to failure page
        return redirect('accounts:visitor_payment_failed')
        
    except Exception as e:
        return redirect('accounts:visitor_payment_failed')


def send_visitor_communication(visitor_payment):
    """
    Send the message/call after visitor payment is completed
    """
    try:
        from apps.interactions.services import InteractionService
        
        qr = visitor_payment.qr_code
        gateway = qr.gateway
        
        if not gateway:
            return
        
        interaction_service = InteractionService()
        
        # Send the communication
        result = interaction_service.initiate_communication(
            gateway=gateway,
            channel=visitor_payment.channel,
            message=visitor_payment.message_content,
            intent=visitor_payment.intent,
            session_data={
                'visitor_payment_id': str(visitor_payment.id),
                'paid_by': 'visitor',
                'amount': float(visitor_payment.amount)
            }
        )
        
        if result['success']:
            visitor_payment.communication_sent = True
            visitor_payment.communication_sent_at = timezone.now()
            visitor_payment.save()
            
    except Exception as e:
        print(f"Error sending visitor communication: {e}")


def visitor_payment_success(request, order_id):
    """Visitor payment success page"""
    try:
        visitor_payment = VisitorPayment.objects.get(order_id=order_id)
        context = {
            'visitor_payment': visitor_payment,
            'qr_code': visitor_payment.qr_code,
        }
        return render(request, 'accounts/visitor_payment_success.html', context)
    except VisitorPayment.DoesNotExist:
        messages.error(request, 'Payment not found')
        return redirect('core:home')


def visitor_payment_failed(request):
    """Visitor payment failed page"""
    return render(request, 'accounts/visitor_payment_failed.html')
