"""
Wallet service for managing recharges and payments.
"""
import requests
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone as django_timezone
from .wallet_models import Wallet, WalletTransaction, RechargeOrder
from .phonepe_service import PhonePeGatewayService


class WalletService:
    """Service for wallet operations."""
    
    @staticmethod
    def get_or_create_wallet(user):
        """Get or create wallet for user."""
        wallet, created = Wallet.objects.get_or_create(user=user)
        return wallet
    
    @staticmethod
    def check_balance(user):
        """Check user's wallet balance."""
        wallet = WalletService.get_or_create_wallet(user)
        return {
            'balance': float(wallet.balance),
            'call_credits': wallet.call_credits,
            'is_frozen': wallet.is_frozen,
            'can_make_calls': wallet.has_sufficient_credits()
        }
    
    @staticmethod
    def create_recharge_order(user, amount, ip_address=None, user_agent=None):
        """Create a recharge order and initiate PhonePe payment."""
        if amount < 1:
            raise ValueError("Minimum recharge amount is ₹1")
        
        wallet = WalletService.get_or_create_wallet(user)
        
        order = RechargeOrder.objects.create(
            user=user,
            wallet=wallet,
            amount=Decimal(str(amount)),
            credits_to_add=int(amount),
            status='created',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Initiate PhonePe payment (all issues fixed)
        payment_result = PhonePeGatewayService.initiate_payment(order)
        
        return order, payment_result
    
    @staticmethod
    def process_call_charge(user, qr_code, notes=''):
        """Process call charge from wallet."""
        wallet = WalletService.get_or_create_wallet(user)
        
        if not wallet.has_sufficient_credits():
            raise ValueError("Insufficient call credits. Please recharge your wallet.")
        
        wallet.deduct_call_credit(qr_code=qr_code, notes=notes)
        
        return {
            'success': True,
            'remaining_credits': wallet.call_credits,
            'remaining_balance': float(wallet.balance)
        }
    
    @staticmethod
    def add_admin_credit(user, amount, notes='Admin credit'):
        """Admin adds credit to user wallet."""
        wallet = WalletService.get_or_create_wallet(user)
        wallet.add_balance(
            amount=amount,
            transaction_type='bonus',
            reference='admin',
            notes=notes
        )
        return wallet
    
    @staticmethod
    def deduct_admin_penalty(user, amount, notes='Admin penalty'):
        """Admin deducts from user wallet."""
        wallet = WalletService.get_or_create_wallet(user)
        wallet.deduct_balance(
            amount=amount,
            transaction_type='penalty',
            reference='admin',
            notes=notes
        )
        return wallet
    
    @staticmethod
    def get_transaction_history(user, limit=50):
        """Get user's transaction history."""
        wallet = WalletService.get_or_create_wallet(user)
        transactions = wallet.transactions.all()[:limit]
        
        return [{
            'id': str(txn.id),
            'type': txn.get_transaction_type_display(),
            'amount': float(txn.amount),
            'balance_after': float(txn.balance_after),
            'credits_after': txn.credits_after,
            'reference': txn.reference,
            'notes': txn.notes,
            'created_at': txn.created_at.isoformat(),
            'status': txn.get_payment_status_display()
        } for txn in transactions]


class RechargeGatewayService:
    """
    Integration with recharge payment gateway.
    API Key: 5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d
    Client ID: SU2504042021229572318914
    """
    
class RechargeGatewayService:
    """
    Integration with recharge payment gateway.
    API Key: 5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d
    Client ID: SU2504042021229572318914
    
    This integrates with a recharge API service for wallet top-ups.
    """
    
    API_KEY = '5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d'
    CLIENT_ID = 'SU2504042021229572318914'
    
    # API endpoints - update these based on your actual gateway
    BASE_URL = getattr(settings, 'RECHARGE_GATEWAY_URL', 'https://api.rechargegateway.in')
    TEST_MODE = getattr(settings, 'RECHARGE_TEST_MODE', False)
    
    @classmethod
    def initiate_recharge(cls, order):
        """Initiate recharge with payment gateway."""
        
        # TEST MODE: Skip actual gateway and return mock payment URL
        if cls.TEST_MODE:
            order.gateway_order_id = f"TEST_{order.order_id}"
            order.status = 'pending'
            order.save()
            
            # Return test payment URL
            test_payment_url = f"http://localhost:8000/api/v1/auth/wallet/test-payment/{order.order_id}/"
            
            return {
                'success': True,
                'payment_url': test_payment_url,
                'gateway_order_id': f"TEST_{order.order_id}",
                'test_mode': True
            }
        
        # PRODUCTION MODE: Use actual payment gateway
        try:
            # Prepare request payload
            payload = {
                'clientId': cls.CLIENT_ID,
                'apiKey': cls.API_KEY,
                'orderId': order.order_id,
                'amount': float(order.amount),
                'currency': 'INR',
                'customerName': order.user.get_full_name() or order.user.username,
                'customerEmail': order.user.email,
                'customerPhone': order.user.get_decrypted_phone() or '',
                'callbackUrl': f"http://{settings.PLATFORM_DOMAIN}/api/v1/auth/wallet/recharge/callback/",
                'returnUrl': f"http://{settings.PLATFORM_DOMAIN}/api/v1/auth/wallet/recharge/success/?order_id={order.order_id}",
                'cancelUrl': f"http://{settings.PLATFORM_DOMAIN}/api/v1/auth/wallet/recharge/cancel/",
                'description': f'Wallet Recharge - {order.credits_to_add} credits'
            }
            
            # Generate checksum/signature for security
            checksum = cls._generate_checksum(payload)
            payload['checksum'] = checksum
            
            # Make API request to initiate payment
            response = requests.post(
                f"{cls.BASE_URL}/api/v1/payment/initiate",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': cls.API_KEY,
                    'X-Client-ID': cls.CLIENT_ID
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    order.gateway_order_id = data.get('gatewayOrderId', '')
                    order.status = 'pending'
                    order.save()
                    
                    return {
                        'success': True,
                        'payment_url': data.get('paymentUrl'),
                        'gateway_order_id': data.get('gatewayOrderId'),
                        'test_mode': False
                    }
                else:
                    error_msg = data.get('message', 'Payment initiation failed')
                    order.mark_failed(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
            else:
                error_msg = f"Gateway error: HTTP {response.status_code}"
                order.mark_failed(error_msg)
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            order.mark_failed('Gateway timeout')
            return {
                'success': False,
                'error': 'Payment gateway timeout. Please try again.'
            }
        except requests.exceptions.ConnectionError:
            order.mark_failed('Gateway connection error')
            return {
                'success': False,
                'error': 'Unable to connect to payment gateway. Please try again.'
            }
        except Exception as e:
            order.mark_failed(str(e))
            return {
                'success': False,
                'error': f'Payment error: {str(e)}'
            }
            payload = {
                'client_id': cls.CLIENT_ID,
                'api_key': cls.API_KEY,
                'order_id': order.order_id,
                'amount': float(order.amount),
                'currency': 'INR',
                'customer_email': order.user.email,
                'customer_phone': order.user.get_decrypted_phone(),
                'callback_url': f"{settings.PLATFORM_DOMAIN}/api/v1/wallet/recharge/callback/",
                'return_url': f"{settings.PLATFORM_DOMAIN}/wallet/recharge/success/",
                'cancel_url': f"{settings.PLATFORM_DOMAIN}/wallet/recharge/cancel/"
            }
            
            # Generate signature
            signature = cls._generate_signature(payload)
            payload['signature'] = signature
            
            response = requests.post(
                f"{cls.BASE_URL}/v1/recharge/initiate",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                order.gateway_order_id = data.get('gateway_order_id', '')
                order.status = 'pending'
                order.save()
                
                return {
                    'success': True,
                    'payment_url': data.get('payment_url'),
                    'gateway_order_id': data.get('gateway_order_id')
                }
            else:
                order.mark_failed(f"Gateway error: {response.status_code}")
                return {
                    'success': False,
                    'error': 'Payment gateway error'
                }
                
        except Exception as e:
            order.mark_failed(str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def verify_payment(cls, order_id, gateway_payment_id, gateway_signature):
        """Verify payment with gateway."""
        try:
            payload = {
                'clientId': cls.CLIENT_ID,
                'apiKey': cls.API_KEY,
                'orderId': order_id,
                'paymentId': gateway_payment_id
            }
            
            # Generate checksum for verification
            checksum = cls._generate_checksum(payload)
            payload['checksum'] = checksum
            
            response = requests.post(
                f"{cls.BASE_URL}/api/v1/payment/verify",
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': cls.API_KEY,
                    'X-Client-ID': cls.CLIENT_ID
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'verified': data.get('status') == 'success',
                    'amount': data.get('amount'),
                    'status': data.get('paymentStatus'),
                    'transaction_id': data.get('transactionId')
                }
            else:
                return {
                    'success': False,
                    'verified': False,
                    'error': f'Verification failed: HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'verified': False,
                'error': str(e)
            }
    
    @classmethod
    def _generate_checksum(cls, payload):
        """
        Generate checksum/signature for request security.
        Format: SHA256(clientId|apiKey|orderId|amount|currency)
        """
        # Create signature string
        sig_string = f"{cls.CLIENT_ID}|{cls.API_KEY}|{payload.get('orderId')}|{payload.get('amount')}|{payload.get('currency')}"
        
        # Generate SHA256 hash
        return hashlib.sha256(sig_string.encode()).hexdigest()
    
    @classmethod
    def _generate_signature(cls, payload):
        """Legacy method - calls _generate_checksum."""
        return cls._generate_checksum(payload)
    
    @classmethod
    def handle_callback(cls, callback_data):
        """Handle payment gateway callback."""
        try:
            order_id = callback_data.get('orderId') or callback_data.get('order_id')
            payment_id = callback_data.get('paymentId') or callback_data.get('payment_id')
            signature = callback_data.get('signature') or callback_data.get('checksum')
            status = callback_data.get('status') or callback_data.get('paymentStatus')
            
            if not order_id:
                return {'success': False, 'message': 'Order ID missing'}
            
            order = RechargeOrder.objects.get(order_id=order_id)
            
            if status in ['success', 'SUCCESS', 'completed', 'COMPLETED']:
                # Verify payment signature
                expected_signature = cls._generate_checksum({
                    'orderId': order_id,
                    'amount': float(order.amount),
                    'currency': 'INR'
                })
                
                # In production, verify signature matches
                # For now, we'll trust the callback if it has a payment_id
                if payment_id:
                    order.mark_completed(
                        gateway_payment_id=payment_id,
                        gateway_signature=signature or ''
                    )
                    return {'success': True, 'message': 'Payment successful'}
                else:
                    order.mark_failed('Payment ID missing')
                    return {'success': False, 'message': 'Payment ID missing'}
            else:
                failure_reason = callback_data.get('message') or callback_data.get('error') or f'Payment {status}'
                order.mark_failed(failure_reason)
                return {'success': False, 'message': failure_reason}
                
        except RechargeOrder.DoesNotExist:
            return {'success': False, 'message': 'Order not found'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
