"""
Debug script for distributor OTP issues.
Run this to check OTP cache and verification.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.core.cache import cache
from apps.accounts.phone_auth import send_otp, verify_otp
import hashlib

def hash_otp(otp):
    """Hash OTP the same way the service does."""
    return hashlib.sha256(otp.encode()).hexdigest()

def test_otp_flow(phone_number):
    """Test complete OTP flow."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING OTP FLOW FOR: {phone_number}")
    print(f"{'='*60}\n")
    
    # Step 1: Send OTP
    print("📤 Step 1: Sending OTP...")
    success, message = send_otp(phone_number)
    print(f"   Result: {'SUCCESS' if success else 'FAILED'}")
    print(f"   Message: {message}\n")
    
    if not success:
        print("❌ Failed to send OTP. Stopping test.")
        return
    
    # Step 2: Check cache
    print("🔍 Step 2: Checking cache...")
    cache_key = f"otp_{phone_number}"
    cache_data = cache.get(cache_key)
    
    if cache_data:
        print(f"   ✅ OTP found in cache")
        print(f"   Attempts remaining: {cache_data.get('attempts')}")
        print(f"   Created at: {cache_data.get('created_at')}")
        print(f"   OTP Hash: {cache_data.get('otp_hash')[:20]}...")
    else:
        print(f"   ❌ OTP NOT found in cache!")
        print(f"   Cache key: {cache_key}")
        return
    
    # Step 3: Get OTP from console output
    print(f"\n📋 Step 3: Manual OTP Entry")
    print(f"   Check the console output above for the OTP")
    print(f"   Look for lines like: '📱 OTP for {phone_number}: XXXXXX'")
    
    otp_input = input(f"\n   Enter the OTP you see in console: ").strip()
    
    if not otp_input:
        print("   ❌ No OTP entered. Stopping test.")
        return
    
    # Step 4: Verify OTP
    print(f"\n🔐 Step 4: Verifying OTP...")
    print(f"   OTP entered: '{otp_input}'")
    print(f"   OTP length: {len(otp_input)}")
    print(f"   OTP is digits: {otp_input.isdigit()}")
    print(f"   OTP hash: {hash_otp(otp_input)[:20]}...")
    
    success, message = verify_otp(phone_number, otp_input)
    print(f"\n   Result: {'SUCCESS ✅' if success else 'FAILED ❌'}")
    print(f"   Message: {message}")
    
    # Step 5: Check cache after verification
    print(f"\n🔍 Step 5: Checking cache after verification...")
    cache_data_after = cache.get(cache_key)
    
    if cache_data_after:
        print(f"   OTP still in cache (failed verification)")
        print(f"   Attempts remaining: {cache_data_after.get('attempts')}")
    else:
        print(f"   OTP removed from cache (successful verification or max attempts)")
    
    print(f"\n{'='*60}")
    print(f"TEST COMPLETE")
    print(f"{'='*60}\n")


def check_cache_for_phone(phone_number):
    """Check what's in cache for a phone number."""
    print(f"\n{'='*60}")
    print(f"🔍 CHECKING CACHE FOR: {phone_number}")
    print(f"{'='*60}\n")
    
    # Check OTP cache
    otp_key = f"otp_{phone_number}"
    otp_data = cache.get(otp_key)
    
    if otp_data:
        print(f"✅ OTP Cache Found:")
        print(f"   Key: {otp_key}")
        print(f"   Attempts: {otp_data.get('attempts')}")
        print(f"   Created: {otp_data.get('created_at')}")
        print(f"   Hash: {otp_data.get('otp_hash')[:30]}...")
    else:
        print(f"❌ No OTP in cache")
        print(f"   Key checked: {otp_key}")
    
    # Check lockout
    lockout_key = f"otp_lockout_{phone_number}"
    is_locked = cache.get(lockout_key)
    
    if is_locked:
        lockout_until = cache.get(f"otp_lockout_until_{phone_number}")
        print(f"\n🔒 ACCOUNT LOCKED")
        print(f"   Locked until: {lockout_until}")
    else:
        print(f"\n🔓 Account not locked")
    
    # Check failed attempts
    failed_key = f"otp_failed_attempts_{phone_number}"
    failed_attempts = cache.get(failed_key, 0)
    print(f"\n📊 Failed Attempts: {failed_attempts}")
    
    # Check cooldown
    cooldown_key = f"otp_resend_cooldown_{phone_number}"
    cooldown = cache.get(cooldown_key)
    
    if cooldown:
        print(f"\n⏱️  Resend Cooldown Active")
        print(f"   Last sent: {cooldown}")
    else:
        print(f"\n✅ No resend cooldown")
    
    print(f"\n{'='*60}\n")


def clear_cache_for_phone(phone_number):
    """Clear all cache entries for a phone number."""
    print(f"\n{'='*60}")
    print(f"🧹 CLEARING CACHE FOR: {phone_number}")
    print(f"{'='*60}\n")
    
    keys_to_clear = [
        f"otp_{phone_number}",
        f"otp_lockout_{phone_number}",
        f"otp_lockout_until_{phone_number}",
        f"otp_failed_attempts_{phone_number}",
        f"otp_resend_cooldown_{phone_number}",
        f"otp_message_id_{phone_number}",
    ]
    
    for key in keys_to_clear:
        cache.delete(key)
        print(f"   ✅ Cleared: {key}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("DISTRIBUTOR OTP DEBUG TOOL")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python test_distributor_otp_debug.py <command> <phone_number>")
        print("\nCommands:")
        print("  test <phone>    - Test complete OTP flow")
        print("  check <phone>   - Check cache status")
        print("  clear <phone>   - Clear cache for phone")
        print("\nExample:")
        print("  python test_distributor_otp_debug.py test 9876543210")
        print("  python test_distributor_otp_debug.py check 9876543210")
        print("  python test_distributor_otp_debug.py clear 9876543210")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if len(sys.argv) < 3:
        print("\n❌ Error: Phone number required")
        print("Example: python test_distributor_otp_debug.py test 9876543210")
        sys.exit(1)
    
    phone = sys.argv[2].strip()
    
    # Validate phone
    if not phone.isdigit() or len(phone) != 10:
        print(f"\n❌ Error: Invalid phone number '{phone}'")
        print("Phone must be 10 digits")
        sys.exit(1)
    
    if command == "test":
        test_otp_flow(phone)
    elif command == "check":
        check_cache_for_phone(phone)
    elif command == "clear":
        clear_cache_for_phone(phone)
    else:
        print(f"\n❌ Unknown command: {command}")
        print("Valid commands: test, check, clear")
        sys.exit(1)
