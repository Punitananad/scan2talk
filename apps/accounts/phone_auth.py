"""
Phone-based authentication for QR activation.
Uses SMSCountry OTP service for mobile verification.
"""
import random
from django.core.cache import cache
from django.utils import timezone as django_timezone
from .models import User


def send_otp(phone_number):
    """
    Generate and send OTP to phone number using SMSCountry.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from apps.communications.otp_service import get_otp_service
    
    otp_service = get_otp_service()
    
    # Send OTP
    success, otp, message = otp_service.send_otp(phone_number)
    
    print(f"\n{'='*60}")
    print(f"📤 SEND OTP RESULT")
    print(f"   Phone: {phone_number}")
    print(f"   Success: {success}")
    print(f"   OTP: {otp}")
    print(f"   Message: {message}")
    print(f"{'='*60}\n")
    
    if success and otp:
        # Store OTP securely
        otp_service.store_otp(phone_number, otp)
        print(f"✅ OTP stored in cache for {phone_number}")
        
        # Verify it was stored
        from django.core.cache import cache
        cache_key = f"otp_{phone_number}"
        cached_data = cache.get(cache_key)
        if cached_data:
            print(f"✅ Verified: OTP is in cache with {cached_data.get('attempts')} attempts")
        else:
            print(f"❌ WARNING: OTP not found in cache after storing!")
        
        return True, "OTP sent successfully"
    else:
        print(f"❌ Failed to send OTP for {phone_number}: {message}")
        return False, message


def verify_otp(phone_number, otp):
    """
    Verify OTP for phone number.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from apps.communications.otp_service import get_otp_service
    from django.core.cache import cache
    
    otp_service = get_otp_service()
    
    # Check if OTP exists in cache first
    cache_key = f"otp_{phone_number}"
    cached_data = cache.get(cache_key)
    
    print(f"\n{'='*60}")
    print(f"🔐 VERIFY OTP")
    print(f"   Phone: {phone_number}")
    print(f"   OTP Entered: '{otp}' (length: {len(otp)})")
    print(f"   Cache Key: {cache_key}")
    print(f"   OTP in Cache: {'YES' if cached_data else 'NO'}")
    if cached_data:
        print(f"   Attempts Remaining: {cached_data.get('attempts')}")
        print(f"   Created At: {cached_data.get('created_at')}")
    print(f"{'='*60}\n")
    
    result = otp_service.verify_otp(phone_number, otp)
    
    print(f"{'='*60}")
    print(f"🔐 VERIFICATION RESULT")
    print(f"   Success: {result[0]}")
    print(f"   Message: {result[1]}")
    print(f"{'='*60}\n")
    
    return result


def resend_otp(phone_number):
    """
    Resend OTP to phone number.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    from apps.communications.otp_service import get_otp_service
    
    otp_service = get_otp_service()
    return otp_service.resend_otp(phone_number)


def get_or_create_user_by_phone(phone_number, name=None):
    """
    Get existing user by phone or create new one.
    """
    # Try to find user by phone
    users = User.objects.all()
    for user in users:
        if user.get_decrypted_phone() == phone_number:
            return user, False
    
    # Create new user
    username = f"user_{phone_number[-6:]}"  # Last 6 digits
    email = f"{username}@vehicle.local"
    
    # Ensure unique username
    counter = 1
    base_username = username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1
    
    user = User.objects.create(
        username=username,
        email=email,
        phone=phone_number,
        is_phone_verified=True,
        first_name=name or '',
    )
    
    return user, True


def mark_phone_verified(phone_number):
    """Mark phone as verified in session."""
    cache_key = f"phone_verified_{phone_number}"
    cache.set(cache_key, True, 1800)  # 30 minutes
    print(f"✅ Marked phone {phone_number} as verified in cache")


def is_phone_verified(phone_number):
    """Check if phone is verified in session."""
    cache_key = f"phone_verified_{phone_number}"
    is_verified = cache.get(cache_key, False)
    print(f"🔍 Checking verification for {phone_number}: {is_verified}")
    return is_verified
