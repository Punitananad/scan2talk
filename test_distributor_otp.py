"""
Test distributor OTP sending - Diagnostic script
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.phone_auth import send_otp, verify_otp
from apps.communications.otp_service import get_otp_service
from django.conf import settings

def test_otp_sending():
    """Test OTP sending for distributor registration."""
    
    print("\n" + "="*60)
    print("🔍 DISTRIBUTOR OTP DIAGNOSTIC TEST")
    print("="*60)
    
    # Check configuration
    print("\n1️⃣ Checking SMSCountry Configuration:")
    print(f"   DEBUG Mode: {settings.DEBUG}")
    print(f"   AUTH_KEY: {getattr(settings, 'SMSCOUNTRY_AUTH_KEY', 'NOT SET')[:10]}...")
    print(f"   AUTH_TOKEN: {'SET' if getattr(settings, 'SMSCOUNTRY_AUTH_TOKEN', None) else 'NOT SET'}")
    
    # Get OTP service
    otp_service = get_otp_service()
    print(f"\n2️⃣ OTP Service Initialized:")
    print(f"   Endpoint: {otp_service.api_endpoint}")
    print(f"   Sender ID: {otp_service.SENDER_ID}")
    
    # Test phone number (use a real number for testing)
    test_phone = input("\n3️⃣ Enter test phone number (10 digits): ").strip()
    
    if not test_phone or len(test_phone) != 10:
        print("❌ Invalid phone number. Must be 10 digits.")
        return
    
    print(f"\n4️⃣ Sending OTP to {test_phone}...")
    success, otp, message = otp_service.send_otp(test_phone)
    
    print(f"\n5️⃣ Result:")
    print(f"   Success: {success}")
    print(f"   Message: {message}")
    
    if success:
        print(f"   OTP Generated: {otp}")
        print(f"\n   ⚠️  In DEBUG mode, OTP is shown here but may not be sent via SMS")
        print(f"   ⚠️  Check console output above for API response details")
        
        # Test verification
        test_verify = input("\n6️⃣ Enter OTP to verify (or press Enter to skip): ").strip()
        
        if test_verify:
            # Store OTP first
            otp_service.store_otp(test_phone, otp)
            
            verify_success, verify_message = otp_service.verify_otp(test_phone, test_verify)
            print(f"\n7️⃣ Verification Result:")
            print(f"   Success: {verify_success}")
            print(f"   Message: {verify_message}")
    else:
        print(f"\n   ❌ Failed to send OTP")
        print(f"   ❌ Error: {message}")
    
    print("\n" + "="*60)
    print("✅ Diagnostic test complete")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_otp_sending()
