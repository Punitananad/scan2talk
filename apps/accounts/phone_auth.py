"""
Phone-based authentication for QR activation.
"""
import random
from django.core.cache import cache
from django.utils import timezone as django_timezone
from .models import User


def generate_otp():
    """Generate a 6-digit OTP."""
    # For development/testing, always return 1234
    return "1234"
    # For production, use random OTP:
    # return str(random.randint(100000, 999999))


def send_otp(phone_number):
    """
    Generate and send OTP to phone number.
    For development, just store in cache and print to console.
    """
    otp = generate_otp()
    
    # Store OTP in cache for 5 minutes
    cache_key = f"otp_{phone_number}"
    cache.set(cache_key, otp, 300)  # 5 minutes
    
    # In development, print to console
    print(f"\n{'='*50}")
    print(f"OTP for {phone_number}: {otp}")
    print(f"{'='*50}\n")
    
    # TODO: In production, integrate with Twilio/SMS service
    # from apps.communications.adapters.sms_adapter import SMSAdapter
    # sms = SMSAdapter()
    # sms.send(phone_number, f"Your OTP is: {otp}")
    
    return True


def verify_otp(phone_number, otp):
    """Verify OTP for phone number."""
    cache_key = f"otp_{phone_number}"
    stored_otp = cache.get(cache_key)
    
    if stored_otp and stored_otp == otp:
        # Clear OTP after successful verification
        cache.delete(cache_key)
        return True
    
    return False


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
    cache.set(cache_key, True, 600)  # 10 minutes


def is_phone_verified(phone_number):
    """Check if phone is verified in session."""
    cache_key = f"phone_verified_{phone_number}"
    return cache.get(cache_key, False)
