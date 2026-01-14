"""
SMSCountry OTP Service - AuthKey-based REST API Integration
Strict compliance with India DLT rules and SMSCountry specifications.
"""
import random
import hashlib
import base64
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import requests

logger = logging.getLogger(__name__)


class SMSCountryOTPService:
    """
    SMSCountry OTP service using REST API with AuthKey authentication.
    NO Account SID - uses only AuthKey + AuthToken for Basic Auth.
    """
    
    # Fixed configuration as per SMSCountry specs
    API_ENDPOINT = "https://restapi.smscountry.com/v0.1/SMSes/"
    SENDER_ID = "SCNTLK"
    DLT_TEMPLATE_ID = "1707176830112398745"
    TOOL = "API"
    
    # DLT-approved message template (MUST NOT BE MODIFIED)
    MESSAGE_TEMPLATE = "Your OTP for Scan2Talk website registration is {otp}. Do not share it with anyone. - Scan2Talk"
    
    # OTP configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 5
    MAX_VERIFICATION_ATTEMPTS = 3
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.auth_key = getattr(settings, 'SMSCOUNTRY_AUTH_KEY', None)
        self.auth_token = getattr(settings, 'SMSCOUNTRY_AUTH_TOKEN', None)
        
        if not self.auth_key or not self.auth_token:
            logger.warning("SMSCountry credentials not configured. OTP sending will fail.")
    
    def _get_auth_header(self):
        """
        Generate Basic Authentication header.
        Format: Basic base64(AuthKey:AuthToken)
        """
        credentials = f"{self.auth_key}:{self.auth_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def generate_otp(self):
        """Generate a secure random 6-digit OTP."""
        return ''.join([str(random.randint(0, 9)) for _ in range(self.OTP_LENGTH)])
    
    def hash_otp(self, otp):
        """Hash OTP for secure storage using SHA-256."""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    def send_otp(self, phone_number, otp=None):
        """
        Send OTP via SMSCountry REST API.
        
        Args:
            phone_number: 10-digit mobile number (without country code)
            otp: Optional OTP (if None, generates new one)
        
        Returns:
            tuple: (success: bool, otp: str, message: str)
        """
        # Generate OTP if not provided
        if not otp:
            otp = self.generate_otp()
        
        # Validate phone number (must be 10 digits)
        phone_number = str(phone_number).strip()
        if not phone_number.isdigit() or len(phone_number) != 10:
            return False, None, "Invalid phone number format. Must be 10 digits."
        
        # Check credentials - if not configured, use dev mode
        if not self.auth_key or not self.auth_token:
            logger.warning("SMSCountry credentials not configured")
            # In development, allow OTP generation without sending
            if settings.DEBUG:
                logger.warning(f"DEV MODE: OTP {otp} for {phone_number} (not sent)")
                print(f"\n{'='*50}")
                print(f"📱 OTP for {phone_number}: {otp}")
                print(f"{'='*50}\n")
                return True, otp, "OTP generated (dev mode - not sent)"
            return False, None, "SMS service not configured"
        
        # Prepare message with OTP
        message_text = self.MESSAGE_TEMPLATE.format(otp=otp)
        
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._get_auth_header()
        }
        
        payload = {
            "Text": message_text,
            "Number": f"91{phone_number}",  # Add India country code
            "SenderId": self.SENDER_ID,
            "DLTTemplateId": self.DLT_TEMPLATE_ID,
            "Tool": self.TOOL
        }
        
        try:
            logger.info(f"Sending OTP to {phone_number} via SMSCountry")
            
            response = requests.post(
                self.API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Log response
            logger.info(f"SMSCountry Response: {response.status_code} - {response.text}")
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"OTP sent successfully to {phone_number}")
                return True, otp, "OTP sent successfully"
            else:
                logger.error(f"SMSCountry API error: {response.status_code} - {response.text}")
                # In dev mode, still return success for testing
                if settings.DEBUG:
                    logger.warning(f"DEV MODE: Ignoring API error, OTP {otp} for {phone_number}")
                    print(f"\n{'='*50}")
                    print(f"📱 OTP for {phone_number}: {otp}")
                    print(f"{'='*50}\n")
                    return True, otp, "OTP generated (dev mode - API error ignored)"
                return False, None, f"Failed to send OTP: {response.text}"
                
        except requests.exceptions.Timeout:
            logger.error("SMSCountry API timeout")
            if settings.DEBUG:
                return True, otp, "OTP generated (dev mode - timeout ignored)"
            return False, None, "SMS service timeout. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"SMSCountry API request failed: {str(e)}")
            if settings.DEBUG:
                return True, otp, "OTP generated (dev mode - request error ignored)"
            return False, None, "Failed to send OTP. Please try again."
        except Exception as e:
            logger.error(f"Unexpected error sending OTP: {str(e)}")
            if settings.DEBUG:
                return True, otp, "OTP generated (dev mode - error ignored)"
            return False, None, "An error occurred. Please try again."
    
    def store_otp(self, phone_number, otp):
        """
        Store OTP securely in cache with expiry.
        
        Storage format:
        - Key: otp_{phone_number}
        - Value: {
            'otp_hash': hashed OTP,
            'attempts': remaining attempts,
            'created_at': timestamp
          }
        """
        otp_hash = self.hash_otp(otp)
        
        cache_key = f"otp_{phone_number}"
        cache_data = {
            'otp_hash': otp_hash,
            'attempts': self.MAX_VERIFICATION_ATTEMPTS,
            'created_at': timezone.now().isoformat()
        }
        
        # Store for 5 minutes
        cache.set(cache_key, cache_data, self.OTP_EXPIRY_MINUTES * 60)
        logger.info(f"OTP stored for {phone_number}, expires in {self.OTP_EXPIRY_MINUTES} minutes")
    
    def verify_otp(self, phone_number, otp):
        """
        Verify OTP for phone number.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        cache_key = f"otp_{phone_number}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return False, "OTP expired or not found. Please request a new OTP."
        
        # Check attempts
        if cache_data['attempts'] <= 0:
            cache.delete(cache_key)
            return False, "Maximum verification attempts exceeded. Please request a new OTP."
        
        # Verify OTP
        otp_hash = self.hash_otp(otp)
        if otp_hash == cache_data['otp_hash']:
            # Success - delete OTP
            cache.delete(cache_key)
            logger.info(f"OTP verified successfully for {phone_number}")
            return True, "OTP verified successfully"
        else:
            # Failed - decrement attempts
            cache_data['attempts'] -= 1
            remaining = cache_data['attempts']
            
            if remaining > 0:
                cache.set(cache_key, cache_data, self.OTP_EXPIRY_MINUTES * 60)
                return False, f"Invalid OTP. {remaining} attempt(s) remaining."
            else:
                cache.delete(cache_key)
                return False, "Invalid OTP. Maximum attempts exceeded."
    
    def invalidate_otp(self, phone_number):
        """Invalidate/delete OTP for phone number."""
        cache_key = f"otp_{phone_number}"
        cache.delete(cache_key)
        logger.info(f"OTP invalidated for {phone_number}")
    
    def resend_otp(self, phone_number):
        """
        Resend OTP (generates new OTP and invalidates old one).
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Invalidate old OTP
        self.invalidate_otp(phone_number)
        
        # Generate and send new OTP
        success, otp, message = self.send_otp(phone_number)
        
        if success:
            self.store_otp(phone_number, otp)
            return True, "New OTP sent successfully"
        else:
            return False, message


# Singleton instance
_otp_service = None

def get_otp_service():
    """Get singleton OTP service instance."""
    global _otp_service
    if _otp_service is None:
        _otp_service = SMSCountryOTPService()
    return _otp_service
