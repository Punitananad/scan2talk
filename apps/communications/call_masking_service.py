"""
Call Masking Service Layer
Provides high-level functions for call masking operations.
"""
from .adapters.call_masking_adapter import CallMaskingAdapter
import logging

logger = logging.getLogger(__name__)


def create_masked_call_for_qr(qr_code_obj):
    """
    Create a masked call URL for a QR code owner.
    
    Args:
        qr_code_obj: PreGeneratedQR instance with owner and gateway
        
    Returns:
        dict: {
            'success': bool,
            'pin': str,
            'call_url': str,
            'expires_in_minutes': int,
            'error': str (if failed)
        }
    """
    if not qr_code_obj.owner:
        return {
            'success': False,
            'error': 'QR code has no owner'
        }
    
    if not qr_code_obj.gateway:
        return {
            'success': False,
            'error': 'QR code not activated'
        }
    
    # Get owner's phone number
    owner_phone = qr_code_obj.owner.get_decrypted_phone()
    if not owner_phone:
        return {
            'success': False,
            'error': 'Owner phone number not available'
        }
    
    # Create masked call
    adapter = CallMaskingAdapter()
    result = adapter.create_masked_call(
        owner_phone_number=owner_phone,
        qr_id=qr_code_obj.qr_code
    )
    
    return result


def create_masked_call(owner_phone_number, qr_id):
    """
    Create a masked call URL (direct function).
    
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
    adapter = CallMaskingAdapter()
    return adapter.create_masked_call(owner_phone_number, qr_id)


def get_pin_info(pin):
    """
    Get information about a PIN mapping.
    
    Args:
        pin (str): The PIN to lookup
        
    Returns:
        dict or None: PIN mapping info if exists and not expired
    """
    adapter = CallMaskingAdapter()
    return adapter.get_pin_info(pin)


def invalidate_pin(pin):
    """
    Invalidate a PIN before its natural expiry.
    
    Args:
        pin (str): The PIN to invalidate
    """
    adapter = CallMaskingAdapter()
    adapter.invalidate_pin(pin)
