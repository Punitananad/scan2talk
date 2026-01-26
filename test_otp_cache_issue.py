"""
Test script to diagnose OTP cache storage issue.
Run this to check if OTP is being stored and retrieved correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.core.cache import cache
from apps.communications.otp_service import get_otp_service
import time

def test_otp_storage():
    """Test OTP storage and retrieval."""
    print("\n" + "="*60)
    print("🧪 TESTING OTP CACHE STORAGE")
    print("="*60 + "\n")
    
    otp_service = get_otp_service()
    test_phone = "9999999999"
    
    # Clear any existing OTP
    cache_key = f"otp_{test_phone}"
    cache.delete(cache_key)
    print(f"1️⃣  Cleared cache for {test_phone}")
    
    # Generate OTP
    test_otp = otp_service.generate_otp()
    print(f"2️⃣  Generated OTP: {test_otp}")
    
    # Store OTP
    print(f"3️⃣  Storing OTP...")
    otp_service.store_otp(test_phone, test_otp)
    
    # Immediately check if stored
    print(f"4️⃣  Checking cache immediately...")
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"   ✅ OTP found in cache!")
        print(f"   - Attempts: {cached_data.get('attempts')}")
        print(f"   - Created: {cached_data.get('created_at')}")
    else:
        print(f"   ❌ OTP NOT found in cache!")
    
    # Wait 100ms and check again
    time.sleep(0.1)
    print(f"5️⃣  Checking cache after 100ms...")
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"   ✅ OTP found in cache!")
    else:
        print(f"   ❌ OTP NOT found in cache!")
    
    # Try to verify
    print(f"6️⃣  Verifying OTP...")
    success, message = otp_service.verify_otp(test_phone, test_otp)
    print(f"   Result: {success}")
    print(f"   Message: {message}")
    
    # Check cache backend
    print(f"\n7️⃣  Cache Backend Info:")
    from django.conf import settings
    print(f"   Backend: {settings.CACHES['default']['BACKEND']}")
    print(f"   Location: {settings.CACHES['default'].get('LOCATION', 'N/A')}")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_otp_storage()
