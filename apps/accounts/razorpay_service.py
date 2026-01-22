"""
Razorpay Payment Gateway Integration
"""
import razorpay
import hmac
import hashlib
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class RazorpayGatewayService:
    """
    Razorpay payment gateway integration for wallet recharge.
    """
    
    def __init__(self):
        self.key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        self.key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        self.webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
        
        if not self.key_id or not self.key_secret:
            logger.warning("Razorpay credentials not configured")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
    
    @classmethod
    def initiate_payment(cls, order):
        """
        Create Razorpay order and return payment URL.
        
        Args:
            order: RechargeOrder instance
            
        Returns:
            dict: {
                'success': bool,
                'payment_url': str,
                'razorpay_order_id': str,
                'error': str (if failed)
            }
        """
        try:
            service = cls()
            
            if not service.client:
                return {
                    'success': False,
                    'error': 'Razorpay not configured'
                }
            
            # Create Razorpay order
            razorpay_order = service.client.order.create({
                'amount': int(order.amount * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': order.order_id,
                'notes': {
                    'order_id': order.order_id,
                    'user_id': str(order.user.id),
                    'credits': order.credits_to_add,
                    'type': 'wallet_recharge'
                }
            })
            
            # Save Razorpay order ID
            order.gateway_order_id = razorpay_order['id']
            order.status = 'pending'
            order.save()
            
            # Generate payment URL
            payment_url = f"https://scan2talk.in/api/v1/auth/wallet/razorpay/checkout/?order_id={order.order_id}"
            
            logger.info(f"Razorpay order created: {razorpay_order['id']} for order {order.order_id}")
            
            return {
                'success': True,
                'payment_url': payment_url,
                'razorpay_order_id': razorpay_order['id'],
                'amount': order.amount,
                'key_id': service.key_id
            }
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            order.mark_failed(f"Razorpay error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def verify_payment_signature(cls, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify Razorpay payment signature.
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Signature from Razorpay
            
        Returns:
            bool: True if signature is valid
        """
        try:
            service = cls()
            
            if not service.client:
                return False
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            service.client.utility.verify_payment_signature(params_dict)
            return True
            
        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Razorpay signature verification failed")
            return False
        except Exception as e:
            logger.error(f"Razorpay verification error: {str(e)}")
            return False
    
    @classmethod
    def verify_webhook_signature(cls, payload, signature):
        """
        Verify webhook signature from Razorpay.
        
        Args:
            payload: Raw webhook payload (bytes or string)
            signature: X-Razorpay-Signature header value
            
        Returns:
            bool: True if signature is valid
        """
        try:
            service = cls()
            
            if not service.webhook_secret:
                logger.warning("Webhook secret not configured")
                return False
            
            # Convert payload to bytes if string
            if isinstance(payload, str):
                payload = payload.encode('utf-8')
            
            # Generate expected signature
            expected_signature = hmac.new(
                service.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification error: {str(e)}")
            return False
    
    @classmethod
    def handle_webhook(cls, payload, signature):
        """
        Handle Razorpay webhook callback.
        
        Args:
            payload: Webhook payload dict
            signature: X-Razorpay-Signature header
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'order_id': str (if applicable)
            }
        """
        try:
            from .wallet_models import RechargeOrder
            
            # Verify webhook signature
            # Note: For webhook verification, we need the raw body
            # This should be done in the view before parsing JSON
            
            event = payload.get('event')
            entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
            
            if not entity:
                return {
                    'success': False,
                    'message': 'Invalid webhook payload'
                }
            
            payment_id = entity.get('id')
            razorpay_order_id = entity.get('order_id')
            amount = entity.get('amount', 0) / 100  # Convert paise to rupees
            status = entity.get('status')
            
            logger.info(f"Razorpay webhook: event={event}, payment_id={payment_id}, status={status}")
            
            # Find order by Razorpay order ID
            try:
                order = RechargeOrder.objects.get(gateway_order_id=razorpay_order_id)
            except RechargeOrder.DoesNotExist:
                logger.error(f"Order not found for Razorpay order ID: {razorpay_order_id}")
                return {
                    'success': False,
                    'message': 'Order not found'
                }
            
            # Handle different events
            if event == 'payment.captured':
                # Payment successful
                if status == 'captured':
                    order.mark_completed(
                        gateway_payment_id=payment_id,
                        gateway_signature=''
                    )
                    logger.info(f"Payment captured for order {order.order_id}")
                    return {
                        'success': True,
                        'message': 'Payment captured',
                        'order_id': order.order_id
                    }
            
            elif event == 'payment.failed':
                # Payment failed
                error_description = entity.get('error_description', 'Payment failed')
                order.mark_failed(error_description)
                logger.info(f"Payment failed for order {order.order_id}: {error_description}")
                return {
                    'success': True,
                    'message': 'Payment failure recorded',
                    'order_id': order.order_id
                }
            
            elif event == 'order.paid':
                # Order paid (alternative event)
                order.mark_completed(
                    gateway_payment_id=payment_id,
                    gateway_signature=''
                )
                logger.info(f"Order paid: {order.order_id}")
                return {
                    'success': True,
                    'message': 'Order paid',
                    'order_id': order.order_id
                }
            
            else:
                logger.info(f"Unhandled Razorpay event: {event}")
                return {
                    'success': True,
                    'message': f'Event {event} received'
                }
                
        except Exception as e:
            logger.error(f"Razorpay webhook error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': str(e)
            }
    
    @classmethod
    def fetch_payment(cls, payment_id):
        """
        Fetch payment details from Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            dict: Payment details or None
        """
        try:
            service = cls()
            
            if not service.client:
                return None
            
            payment = service.client.payment.fetch(payment_id)
            return payment
            
        except Exception as e:
            logger.error(f"Failed to fetch payment {payment_id}: {str(e)}")
            return None
    
    @classmethod
    def refund_payment(cls, payment_id, amount=None):
        """
        Refund a payment.
        
        Args:
            payment_id: Razorpay payment ID
            amount: Amount to refund in rupees (None for full refund)
            
        Returns:
            dict: Refund details or error
        """
        try:
            service = cls()
            
            if not service.client:
                return {
                    'success': False,
                    'error': 'Razorpay not configured'
                }
            
            refund_data = {}
            if amount:
                refund_data['amount'] = int(amount * 100)  # Convert to paise
            
            refund = service.client.payment.refund(payment_id, refund_data)
            
            logger.info(f"Refund created: {refund['id']} for payment {payment_id}")
            
            return {
                'success': True,
                'refund_id': refund['id'],
                'amount': refund['amount'] / 100,
                'status': refund['status']
            }
            
        except Exception as e:
            logger.error(f"Refund failed for payment {payment_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
