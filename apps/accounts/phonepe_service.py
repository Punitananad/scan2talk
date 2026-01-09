"""
PhonePe Payment Gateway Integration - PRODUCTION GRADE
Strict spec compliance for PhonePe PG v1 API
"""
import base64
import hashlib
import json
import requests
from uuid import uuid4
from django.conf import settings
from .wallet_models import RechargeOrder


class PhonePeGatewayService:
    """PhonePe PG Integration - Spec-accurate implementation"""
    
    # Credentials
    MERCHANT_ID = getattr(settings, 'PHONEPE_MERCHANT_ID', 'M227BOU8BBNV7')
    SALT_KEY = getattr(settings, 'PHONEPE_SALT_KEY', '5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d')
    SALT_INDEX = getattr(settings, 'PHONEPE_SALT_INDEX', 1)
    
    # Environment
    IS_PRODUCTION = getattr(settings, 'PHONEPE_PRODUCTION', True)
    PROD_URL = 'https://api.phonepe.com/apis/hermes'
    UAT_URL = 'https://api-preprod.phonepe.com/apis/pg-sandbox'
    BASE_URL = PROD_URL if IS_PRODUCTION else UAT_URL
    
    @classmethod
    def initiate_payment(cls, order):
        """
        Initiate PhonePe payment - /pg/v1/pay
        Returns: {'success': bool, 'payment_url': str, 'transaction_id': str}
        """
        try:
            # Generate unique transaction ID (max 35 chars, alphanumeric + underscore)
            transaction_id = f"TXN{uuid4().hex[:28].upper()}"  # Total: 31 chars
            order.gateway_order_id = transaction_id
            order.save()
            
            # Get callback URLs
            domain = settings.PLATFORM_DOMAIN
            protocol = 'https' if cls.IS_PRODUCTION else 'http'
            callback_url = f"{protocol}://{domain}/api/v1/auth/wallet/phonepe/callback/"
            redirect_url = f"{protocol}://{domain}/api/v1/auth/wallet/phonepe/callback/?order_id={order.order_id}"
            
            # Build payload (strict PhonePe spec)
            payload = {
                "merchantId": cls.MERCHANT_ID,
                "merchantTransactionId": transaction_id,
                "merchantUserId": f"U{order.user.id}",  # Keep it short
                "amount": int(float(order.amount) * 100),  # Paise
                "redirectUrl": redirect_url,
                "redirectMode": "POST",
                "callbackUrl": callback_url,
                "paymentInstrument": {
                    "type": "PAY_PAGE"
                }
            }
            
            # Base64 encode payload
            payload_json = json.dumps(payload, separators=(',', ':'))  # No spaces
            payload_base64 = base64.b64encode(payload_json.encode()).decode()
            
            # Generate X-VERIFY (CRITICAL: exact spec)
            x_verify = cls._generate_x_verify_for_pay(payload_base64)
            
            # API request
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': x_verify
            }
            
            request_body = {'request': payload_base64}
            
            # Debug logs
            print(f"\n=== PhonePe Payment Initiation ===")
            print(f"URL: {cls.BASE_URL}/pg/v1/pay")
            print(f"Environment: {'PRODUCTION' if cls.IS_PRODUCTION else 'UAT'}")
            print(f"Merchant ID: {cls.MERCHANT_ID}")
            print(f"Transaction ID: {transaction_id}")
            print(f"Amount: ₹{order.amount} ({payload['amount']} paise)")
            print(f"Payload JSON: {payload_json}")
            print(f"Payload Base64: {payload_base64[:80]}...")
            print(f"X-VERIFY: {x_verify}")
            print(f"Headers: {headers}")
            
            # Make API call
            response = requests.post(
                f"{cls.BASE_URL}/pg/v1/pay",
                json=request_body,
                headers=headers,
                timeout=30
            )
            
            print(f"\n=== PhonePe Response ===")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    payment_url = data.get('data', {}).get('instrumentResponse', {}).get('redirectInfo', {}).get('url')
                    
                    if not payment_url:
                        raise ValueError("Payment URL not found in response")
                    
                    order.status = 'pending'
                    order.save()
                    
                    return {
                        'success': True,
                        'payment_url': payment_url,
                        'transaction_id': transaction_id,
                        'gateway_order_id': transaction_id
                    }
                else:
                    error_code = data.get('code', 'UNKNOWN')
                    error_msg = data.get('message', 'Payment initiation failed')
                    full_error = f"PhonePe Error {error_code}: {error_msg}"
                    
                    print(f"ERROR: {full_error}")
                    order.mark_failed(full_error)
                    
                    return {
                        'success': False,
                        'error': full_error,
                        'code': error_code
                    }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"ERROR: {error_msg}")
                order.mark_failed(error_msg)
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            print(f"ERROR: {error_msg}")
            order.mark_failed(error_msg)
            
            return {
                'success': False,
                'error': error_msg
            }
    
    @classmethod
    def _generate_x_verify_for_pay(cls, payload_base64):
        """
        Generate X-VERIFY for /pg/v1/pay endpoint
        
        PhonePe Spec (EXACT):
        X-VERIFY = SHA256(base64_payload + endpoint + salt_key) + "###" + salt_index
        
        Where:
        - base64_payload: Base64 encoded JSON payload
        - endpoint: "/pg/v1/pay" (WITH leading slash)
        - salt_key: Your salt key from dashboard
        - salt_index: Usually 1
        """
        endpoint = "/pg/v1/pay"
        string_to_hash = f"{payload_base64}{endpoint}{cls.SALT_KEY}"
        sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        x_verify = f"{sha256_hash}###{cls.SALT_INDEX}"
        
        print(f"\n=== X-VERIFY Generation ===")
        print(f"Payload Base64 (first 50): {payload_base64[:50]}")
        print(f"Endpoint: {endpoint}")
        print(f"Salt Key (first 10): {cls.SALT_KEY[:10]}...")
        print(f"Salt Index: {cls.SALT_INDEX}")
        print(f"String to hash (first 100): {string_to_hash[:100]}...")
        print(f"SHA256 Hash: {sha256_hash}")
        print(f"X-VERIFY: {x_verify}")
        
        return x_verify
    
    @classmethod
    def _generate_x_verify_for_status(cls, merchant_id, transaction_id):
        """
        Generate X-VERIFY for /pg/v1/status endpoint
        
        PhonePe Spec:
        X-VERIFY = SHA256(endpoint + salt_key) + "###" + salt_index
        
        Where endpoint = f"/pg/v1/status/{merchant_id}/{transaction_id}"
        """
        endpoint = f"/pg/v1/status/{merchant_id}/{transaction_id}"
        string_to_hash = f"{endpoint}{cls.SALT_KEY}"
        sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        x_verify = f"{sha256_hash}###{cls.SALT_INDEX}"
        
        return x_verify
    
    @classmethod
    def check_payment_status(cls, transaction_id):
        """Check payment status"""
        try:
            x_verify = cls._generate_x_verify_for_status(cls.MERCHANT_ID, transaction_id)
            
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': x_verify,
                'X-MERCHANT-ID': cls.MERCHANT_ID
            }
            
            endpoint = f"/pg/v1/status/{cls.MERCHANT_ID}/{transaction_id}"
            response = requests.get(
                f"{cls.BASE_URL}{endpoint}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def handle_callback(cls, callback_data):
        """
        Handle PhonePe callback
        
        Callback X-VERIFY format (DIFFERENT from /pay):
        X-VERIFY = SHA256(base64_response + salt_key) + "###" + salt_index
        """
        try:
            response_base64 = callback_data.get('response', '')
            
            if not response_base64:
                return {'success': False, 'message': 'No response data'}
            
            # Verify checksum
            x_verify_received = callback_data.get('X-VERIFY') or callback_data.get('x-verify')
            x_verify_calculated = cls._generate_callback_checksum(response_base64)
            
            # Decode response
            response_json = base64.b64decode(response_base64).decode()
            response_data = json.loads(response_json)
            
            transaction_id = response_data.get('data', {}).get('merchantTransactionId')
            payment_code = response_data.get('code')
            
            if not transaction_id:
                return {'success': False, 'message': 'Transaction ID missing'}
            
            # Find order
            try:
                order = RechargeOrder.objects.get(gateway_order_id=transaction_id)
            except RechargeOrder.DoesNotExist:
                return {'success': False, 'message': 'Order not found'}
            
            # Process payment
            if payment_code == 'PAYMENT_SUCCESS':
                payment_id = response_data.get('data', {}).get('transactionId', '')
                order.mark_completed(
                    gateway_payment_id=payment_id,
                    gateway_signature=x_verify_received or ''
                )
                
                return {
                    'success': True,
                    'message': 'Payment successful',
                    'order_id': order.order_id
                }
            else:
                failure_reason = response_data.get('message', f'Payment {payment_code}')
                order.mark_failed(failure_reason)
                
                return {
                    'success': False,
                    'message': failure_reason,
                    'order_id': order.order_id
                }
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @classmethod
    def _generate_callback_checksum(cls, response_base64):
        """
        Generate checksum for callback verification
        
        PhonePe Callback Spec:
        X-VERIFY = SHA256(base64_response + salt_key) + "###" + salt_index
        
        Note: NO endpoint in callback checksum (different from /pay)
        """
        string_to_hash = f"{response_base64}{cls.SALT_KEY}"
        sha256_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        return f"{sha256_hash}###{cls.SALT_INDEX}"
