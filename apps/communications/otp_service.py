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
    Uses account-scoped endpoint: /Accounts/{AuthKey}/SMSes/
    """
    
    # Configuration
    SENDER_ID = "SCNTLK"
    TOOL = "API"
    
    # OTP configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 5
    MAX_VERIFICATION_ATTEMPTS = 3
    RESEND_COOLDOWN_SECONDS = 30  # 30 seconds between resends
    LOCKOUT_DURATION_HOURS = 2  # 2 hours lockout after max failed attempts
    MAX_FAILED_ATTEMPTS = 3  # Max failed verification attempts before lockout
    
    def __init__(self):
        """Initialize with credentials from environment."""
        self.auth_key = getattr(settings, 'SMSCOUNTRY_AUTH_KEY', None)
        self.auth_token = getattr(settings, 'SMSCOUNTRY_AUTH_TOKEN', None)
        
        # CRITICAL: Account-scoped endpoint (includes AuthKey in URL)
        if self.auth_key:
            self.api_endpoint = f"https://restapi.smscountry.com/v0.1/Accounts/{self.auth_key}/SMSes/"
        else:
            self.api_endpoint = None
        
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
        Send OTP via SMSCountry REST API with rate limiting.
        
        Args:
            phone_number: 10-digit mobile number (without country code)
            otp: Optional OTP (if None, generates new one)
        
        Returns:
            tuple: (success: bool, otp: str, message: str)
        """
        # Check if phone is locked out
        lockout_key = f"otp_lockout_{phone_number}"
        if cache.get(lockout_key):
            lockout_until = cache.get(f"otp_lockout_until_{phone_number}")
            return False, None, f"Too many failed attempts. Please try again after {lockout_until}."
        
        # Check resend cooldown
        cooldown_key = f"otp_resend_cooldown_{phone_number}"
        last_sent = cache.get(cooldown_key)
        if last_sent:
            remaining = self.RESEND_COOLDOWN_SECONDS - (timezone.now() - last_sent).seconds
            if remaining > 0:
                return False, None, f"Please wait {remaining} seconds before requesting a new OTP."
        
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
                # Set cooldown even in dev mode
                cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                return True, otp, "OTP generated (dev mode - not sent)"
            return False, None, "SMS service not configured"
        
        # Prepare message - EXACT format from working Postman request
        message_text = f"Your OTP for Scan2Talk website registration is {otp}. Do not share it with anyone. – Scan2Talk"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._get_auth_header()
        }
        
        payload = {
            "Text": message_text,
            "Number": f"91{phone_number}",
            "SenderId": self.SENDER_ID,
            "DRNotifyUrl": "https://www.scan2talk.in/notifyurl",
            "DRNotifyHttpMethod": "POST",
            "Tool": self.TOOL
        }
        
        try:
            logger.info(f"Sending OTP to {phone_number} via SMSCountry")
            logger.info(f"Using endpoint: {self.api_endpoint}")
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            # Log full response for debugging
            logger.info(f"SMSCountry Response: {response.status_code}")
            logger.info(f"Response Body: {response.text}")
            
            # CRITICAL: Don't trust HTTP 200 blindly - check response body
            try:
                response_data = response.json()
            except ValueError:
                logger.error(f"Invalid JSON response: {response.text}")
                if settings.DEBUG:
                    logger.warning(f"DEV MODE: Invalid JSON, OTP {otp} for {phone_number}")
                    print(f"\n{'='*50}")
                    print(f"📱 OTP for {phone_number}: {otp}")
                    print(f"⚠️  API returned invalid JSON")
                    print(f"{'='*50}\n")
                    cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                    return True, otp, "OTP generated (dev mode - invalid JSON)"
                return False, None, "Invalid response from SMS service"
            
            # Check both HTTP status AND Success field in response
            # IMPORTANT: 202 Accepted means message is queued (this is SUCCESS)
            if response.status_code in [200, 201, 202]:
                # For 202, message might be queued - this is still success
                if response.status_code == 202:
                    logger.info(f"✅ OTP queued for delivery to {phone_number}")
                    # Set resend cooldown
                    cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                    return True, otp, "OTP sent successfully (queued for delivery)"
                
                # For 200/201, check Success field
                if response_data.get("Success") is True:
                    message_id = response_data.get("MessageUUID") or response_data.get("MessageId")
                    logger.info(f"✅ OTP sent successfully to {phone_number}, MessageID: {message_id}")
                    
                    # Store message ID for delivery tracking
                    cache_key = f"otp_message_id_{phone_number}"
                    cache.set(cache_key, message_id, self.OTP_EXPIRY_MINUTES * 60)
                    
                    # Set resend cooldown
                    cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                    
                    return True, otp, "OTP sent successfully"
                elif response_data.get("Success") is False:
                    # API returned 200 but Success=False (DLT rejection, invalid sender, etc.)
                    error_msg = response_data.get("Message") or response_data.get("Error") or response.text
                    logger.error(f"❌ SMSCountry API rejected: {error_msg}")
                    logger.error(f"Full response: {response_data}")
                    
                    # In dev mode, still return success for testing
                    if settings.DEBUG:
                        logger.warning(f"DEV MODE: Ignoring API rejection, OTP {otp} for {phone_number}")
                        print(f"\n{'='*50}")
                        print(f"📱 OTP for {phone_number}: {otp}")
                        print(f"⚠️  API Error: {error_msg}")
                        print(f"{'='*50}\n")
                        cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                        return True, otp, "OTP generated (dev mode - API error ignored)"
                    
                    return False, None, f"SMS delivery failed: {error_msg}"
                else:
                    # Success field not present, assume success for 200/201
                    logger.info(f"✅ OTP sent to {phone_number} (Success field not in response)")
                    cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                    return True, otp, "OTP sent successfully"
            else:
                # Non-2xx status code
                error_msg = response_data.get("Message") or response_data.get("Error") or response.text
                logger.error(f"❌ SMSCountry API error: {error_msg}")
                logger.error(f"Full response: {response_data}")
                
                # In dev mode, still return success for testing
                if settings.DEBUG:
                    logger.warning(f"DEV MODE: Ignoring API error, OTP {otp} for {phone_number}")
                    print(f"\n{'='*50}")
                    print(f"📱 OTP for {phone_number}: {otp}")
                    print(f"⚠️  API Error: {error_msg}")
                    print(f"{'='*50}\n")
                    cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                    return True, otp, "OTP generated (dev mode - API error ignored)"
                
                return False, None, f"SMS delivery failed: {error_msg}"
                
        except requests.exceptions.Timeout:
            logger.error("⏱️  SMSCountry API timeout")
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print(f"📱 OTP for {phone_number}: {otp}")
                print(f"⚠️  API Timeout")
                print(f"{'='*50}\n")
                cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                return True, otp, "OTP generated (dev mode - timeout ignored)"
            return False, None, "SMS service timeout. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"🔌 SMSCountry API request failed: {str(e)}")
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print(f"📱 OTP for {phone_number}: {otp}")
                print(f"⚠️  Request Error: {str(e)}")
                print(f"{'='*50}\n")
                cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
                return True, otp, "OTP generated (dev mode - request error ignored)"
            return False, None, "Failed to send OTP. Please try again."
        except Exception as e:
            logger.error(f"💥 Unexpected error sending OTP: {str(e)}", exc_info=True)
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print(f"📱 OTP for {phone_number}: {otp}")
                print(f"⚠️  Error: {str(e)}")
                print(f"{'='*50}\n")
                cache.set(cooldown_key, timezone.now(), self.RESEND_COOLDOWN_SECONDS)
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
        Verify OTP for phone number with lockout protection.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if phone is locked out
        lockout_key = f"otp_lockout_{phone_number}"
        if cache.get(lockout_key):
            lockout_until = cache.get(f"otp_lockout_until_{phone_number}")
            return False, f"Too many failed attempts. Please try again after {lockout_until}."
        
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
            # Success - delete OTP and clear any failed attempt tracking
            cache.delete(cache_key)
            cache.delete(f"otp_failed_attempts_{phone_number}")
            logger.info(f"OTP verified successfully for {phone_number}")
            return True, "OTP verified successfully"
        else:
            # Failed - decrement attempts
            cache_data['attempts'] -= 1
            remaining = cache_data['attempts']
            
            # Track total failed attempts for lockout
            failed_attempts_key = f"otp_failed_attempts_{phone_number}"
            failed_attempts = cache.get(failed_attempts_key, 0) + 1
            cache.set(failed_attempts_key, failed_attempts, 3600)  # Track for 1 hour
            
            if remaining > 0:
                cache.set(cache_key, cache_data, self.OTP_EXPIRY_MINUTES * 60)
                
                # Check if we should trigger lockout
                if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                    # Lockout for 2 hours
                    lockout_seconds = self.LOCKOUT_DURATION_HOURS * 3600
                    cache.set(lockout_key, True, lockout_seconds)
                    
                    # Calculate lockout end time
                    from datetime import datetime, timedelta
                    lockout_until = (timezone.now() + timedelta(hours=self.LOCKOUT_DURATION_HOURS)).strftime('%I:%M %p')
                    cache.set(f"otp_lockout_until_{phone_number}", lockout_until, lockout_seconds)
                    
                    # Clear OTP data
                    cache.delete(cache_key)
                    
                    logger.warning(f"Phone {phone_number} locked out after {failed_attempts} failed attempts")
                    return False, f"Too many failed attempts. Account locked until {lockout_until}. Please try again later."
                
                return False, f"Invalid OTP. {remaining} attempt(s) remaining."
            else:
                cache.delete(cache_key)
                return False, "Invalid OTP. Maximum attempts exceeded. Please request a new OTP."
    
    def invalidate_otp(self, phone_number):
        """Invalidate/delete OTP for phone number."""
        cache_key = f"otp_{phone_number}"
        cache.delete(cache_key)
        logger.info(f"OTP invalidated for {phone_number}")
    
    def check_delivery_status(self, phone_number):
        """
        Check SMS delivery status using SMSCountry Reports API.
        
        Returns:
            dict: Delivery status information or None
        """
        cache_key = f"otp_message_id_{phone_number}"
        message_id = cache.get(cache_key)
        
        if not message_id or not self.auth_key:
            return None
        
        try:
            # SMSCountry Reports API endpoint
            reports_url = f"https://restapi.smscountry.com/v0.1/Accounts/{self.auth_key}/SMSes/{message_id}"
            
            headers = {
                "Authorization": self._get_auth_header()
            }
            
            response = requests.get(reports_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📊 Delivery status for {phone_number}: {data}")
                return data
            else:
                logger.warning(f"Failed to get delivery status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking delivery status: {str(e)}")
            return None
    
    def resend_otp(self, phone_number):
        """
        Resend OTP (generates new OTP and invalidates old one).
        Enforces 30-second cooldown between resends.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if phone is locked out
        lockout_key = f"otp_lockout_{phone_number}"
        if cache.get(lockout_key):
            lockout_until = cache.get(f"otp_lockout_until_{phone_number}")
            return False, f"Too many failed attempts. Please try again after {lockout_until}."
        
        # Check resend cooldown
        cooldown_key = f"otp_resend_cooldown_{phone_number}"
        last_sent = cache.get(cooldown_key)
        if last_sent:
            elapsed = (timezone.now() - last_sent).seconds
            remaining = self.RESEND_COOLDOWN_SECONDS - elapsed
            if remaining > 0:
                return False, f"Please wait {remaining} seconds before requesting a new OTP."
        
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
