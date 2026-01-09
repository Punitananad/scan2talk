"""
Wallet management views and APIs.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from .wallet_service import WalletService, RechargeGatewayService
from .wallet_models import Wallet, RechargeOrder


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
    """Recharge wallet page - DIRECT ADD (NO PAYMENT GATEWAY)."""
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount', 0))
            
            if amount < 1:
                messages.error(request, 'Minimum recharge amount is ₹1')
                return redirect('accounts:recharge_wallet')
            
            # DIRECT ADD - Skip payment gateway, add balance immediately
            wallet = WalletService.get_or_create_wallet(request.user)
            
            # Add balance directly using the correct method
            wallet.add_balance(
                amount=amount,
                transaction_type='recharge',
                reference='DIRECT_ADD',
                notes=f'Direct recharge ₹{amount} (Test Mode - No Gateway)'
            )
            
            messages.success(request, f'✅ Successfully added ₹{amount} to your wallet! Balance: ₹{wallet.balance}')
            return redirect('accounts:wallet_dashboard')
                
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
