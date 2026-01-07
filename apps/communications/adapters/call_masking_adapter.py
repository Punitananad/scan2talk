"""
SparkTG / TelephonyCloud Call Masking API Adapter
"""
import random
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone as django_timezone
import logging

logger = logging.getLogger(__name__)


class CallMaskingAdapter:
    """
    Adapter for SparkTG Call Masking API integration.
    Handles PIN generation and mapping to owner phone numbers.
    """
    
    DID_NUMBER = "01205019042"
    API_ENDPOINT = "https://telephonycloud.co.in/api/v1/mask"
    PIN_EXPIRY_MINUTES = 10
    
    def __init__(self):
        self.username = getattr(settings, 'SPARKTG_USERNAME', None)
        self.password = getattr(settings, 'SPARKTG_PASSWORD', None)
        
        if not self.username or not self.password:
            logger.warning("SparkTG credentials not configured in settings")
    
    def generate_pin(self):
        """Generate a secure 4-digit PIN."""
        return str(random.randint(1000, 9999))
    
    def create_masked_call(self, owner_phone_number, qr_id):
        """
        Create a masked call mapping for the owner.
        
        Args:
            owner_phone_number (str): Owner's mobile number
            qr_id (str): QR code identifier for tracking
            
        Returns:
            dict: {
                'success': bool,
                'pin': str,
                'call_url': str,
                'expires_in_minutes': int,
                'error': str (if failed)
            }
        """
        try:
            # Generate PIN
            pin = self.generate_pin()
            
            # Prepare request
            auth = (self.username, self.password)
            data = {
                'key': pin,
                'number': owner_phone_number
            }
            
            # Call SparkTG API
            response = requests.post(
                self.API_ENDPOINT,
                auth=auth,
                data=data,
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                # Store PIN mapping in cache for expiry tracking
                cache_key = f"call_mask_pin_{pin}"
                cache.set(cache_key, {
                    'owner_phone': owner_phone_number,
                    'qr_id': qr_id,
                    'created_at': django_timezone.now().isoformat()
                }, self.PIN_EXPIRY_MINUTES * 60)
                
                # Generate call URL
                call_url = f"tel:{self.DID_NUMBER},{pin}#"
                
                logger.info(f"Call mask created: PIN={pin}, QR={qr_id}, Phone={owner_phone_number[-4:]}")
                
                return {
                    'success': True,
                    'pin': pin,
                    'call_url': call_url,
                    'expires_in_minutes': self.PIN_EXPIRY_MINUTES,
                    'did_number': self.DID_NUMBER
                }
            else:
                error_msg = f"API returned status {response.status_code}"
                logger.error(f"SparkTG API error: {error_msg}, Response: {response.text}")
                return {
                    'success': False,
                    'error': error_msg,
                    'details': response.text
                }
                
        except requests.exceptions.Timeout:
            error_msg = "API request timeout"
            logger.error(f"SparkTG API timeout for QR={qr_id}")
            return {
                'success': False,
                'error': error_msg
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(f"SparkTG API error for QR={qr_id}: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Call masking error for QR={qr_id}: {error_msg}", exc_info=True)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_pin_info(self, pin):
        """
        Get information about a PIN mapping.
        
        Args:
            pin (str): The PIN to lookup
            
        Returns:
            dict or None: PIN mapping info if exists and not expired
        """
        cache_key = f"call_mask_pin_{pin}"
        return cache.get(cache_key)
    
    def invalidate_pin(self, pin):
        """
        Invalidate a PIN before its natural expiry.
        
        Args:
            pin (str): The PIN to invalidate
        """
        cache_key = f"call_mask_pin_{pin}"
        cache.delete(cache_key)
        logger.info(f"PIN {pin} invalidated")
