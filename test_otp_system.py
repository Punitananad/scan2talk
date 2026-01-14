#!/usr/bin/env python
"""
Test script for SMSCountry OTP verification system.
Tests OTP generation, sending, verification, and resend functionality.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.communications.otp_service import get_otp_service
from django.core.cache import cache
import time


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_result(test_name, success, message=""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"     {message}")


def test_otp_generation():
    """Test OTP generation."""
    print_header("Test 1: OTP Generation")
    
    otp_service = get_otp_service()
    otp = otp_service.generate_otp()
    
    # Check OTP is 6 digits
    is_valid = len(otp) == 6 and otp.isdigit()
    print_result("OTP Generation", is_valid, f"Generated OTP: {otp}")
    
    # Check uniqueness (generate multiple)
    otps = set([otp_service.generate_otp() for _ in range(10)])
    print_result("OTP Uniqueness", len(otps) > 1, f"Generated {len(otps)} unique OTPs")
    
    return is_valid


def test_otp_hashing():
    """Test OTP hashing."""
    print_header("Test 2: OTP Hashing")
    
    otp_service = get_otp_service()
    otp = "123456"
    
    hash1 = otp_service.hash_otp(otp)
    hash2 = otp_service.hash_otp(otp)
    hash3 = otp_service.hash_otp("654321")
    
    # Same OTP should produce same hash
    same_hash = hash1 == hash2
    print_result("Hash Consistency", same_hash, f"Hash: {hash1[:16]}...")
    
    # Different OTP should produce different hash
    diff_hash = hash1 != hash3
    print_result("Hash Uniqueness", diff_hash)
    
    return same_hash and diff_hash


def test_otp_storage():
    """Test OTP storage in cache."""
    print_header("Test 3: OTP Storage")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    otp = "123456"
    
    # Clear any existing OTP
    cache.delete(f"otp_{phone}")
    
    # Store OTP
    otp_service.store_otp(phone, otp)
    
    # Check if stored
    cache_data = cache.get(f"otp_{phone}")
    is_stored = cache_data is not None
    print_result("OTP Storage", is_stored, f"Stored for phone: {phone}")
    
    # Check structure
    has_hash = 'otp_hash' in cache_data if cache_data else False
    has_attempts = 'attempts' in cache_data if cache_data else False
    has_timestamp = 'created_at' in cache_data if cache_data else False
    
    print_result("Storage Structure", has_hash and has_attempts and has_timestamp,
                f"Attempts: {cache_data.get('attempts', 0)}")
    
    # Cleanup
    cache.delete(f"otp_{phone}")
    
    return is_stored and has_hash


def test_otp_verification():
    """Test OTP verification."""
    print_header("Test 4: OTP Verification")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    otp = "123456"
    
    # Clear cache
    cache.delete(f"otp_{phone}")
    
    # Store OTP
    otp_service.store_otp(phone, otp)
    
    # Test correct OTP
    success, message = otp_service.verify_otp(phone, otp)
    print_result("Correct OTP Verification", success, message)
    
    # Store again for wrong OTP test
    otp_service.store_otp(phone, otp)
    
    # Test wrong OTP
    success2, message2 = otp_service.verify_otp(phone, "654321")
    print_result("Wrong OTP Rejection", not success2, message2)
    
    # Cleanup
    cache.delete(f"otp_{phone}")
    
    return success and not success2


def test_attempt_limiting():
    """Test attempt limiting."""
    print_header("Test 5: Attempt Limiting")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    otp = "123456"
    
    # Clear cache
    cache.delete(f"otp_{phone}")
    
    # Store OTP
    otp_service.store_otp(phone, otp)
    
    # Try wrong OTP 3 times
    attempts = []
    for i in range(4):
        success, message = otp_service.verify_otp(phone, "000000")
        attempts.append((success, message))
        print(f"  Attempt {i+1}: {message}")
    
    # First 3 should fail with remaining attempts
    # 4th should fail with max attempts exceeded
    first_three_failed = all(not s for s, _ in attempts[:3])
    fourth_exceeded = "exceeded" in attempts[3][1].lower()
    
    print_result("Attempt Limiting", first_three_failed and fourth_exceeded)
    
    # Cleanup
    cache.delete(f"otp_{phone}")
    
    return first_three_failed and fourth_exceeded


def test_otp_expiry():
    """Test OTP expiry (simulated)."""
    print_header("Test 6: OTP Expiry")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    otp = "123456"
    
    # Clear cache
    cache.delete(f"otp_{phone}")
    
    # Store OTP with 2 second expiry (for testing)
    cache_key = f"otp_{phone}"
    cache_data = {
        'otp_hash': otp_service.hash_otp(otp),
        'attempts': 3,
        'created_at': '2026-01-14T12:00:00'
    }
    cache.set(cache_key, cache_data, 2)  # 2 seconds
    
    # Verify immediately (should work)
    success1, message1 = otp_service.verify_otp(phone, otp)
    print_result("Immediate Verification", success1, message1)
    
    # Store again
    cache.set(cache_key, cache_data, 2)
    
    # Wait for expiry
    print("  Waiting 3 seconds for expiry...")
    time.sleep(3)
    
    # Try to verify (should fail)
    success2, message2 = otp_service.verify_otp(phone, otp)
    print_result("Expired OTP Rejection", not success2, message2)
    
    # Cleanup
    cache.delete(f"otp_{phone}")
    
    return success1 and not success2


def test_otp_sending():
    """Test OTP sending (dev mode)."""
    print_header("Test 7: OTP Sending (Dev Mode)")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    
    # Send OTP
    success, otp, message = otp_service.send_otp(phone)
    
    print_result("OTP Sending", success, message)
    if otp:
        print(f"     Generated OTP: {otp}")
    
    return success


def test_resend_functionality():
    """Test OTP resend."""
    print_header("Test 8: OTP Resend")
    
    otp_service = get_otp_service()
    phone = "9876543210"
    
    # Clear cache
    cache.delete(f"otp_{phone}")
    
    # Send first OTP
    success1, otp1, message1 = otp_service.send_otp(phone)
    print_result("First OTP Send", success1, f"OTP: {otp1}")
    
    # Resend OTP
    success2, message2 = otp_service.resend_otp(phone)
    print_result("OTP Resend", success2, message2)
    
    # Old OTP should not work
    if success1 and success2:
        success3, message3 = otp_service.verify_otp(phone, otp1)
        print_result("Old OTP Invalidated", not success3, message3)
    
    # Cleanup
    cache.delete(f"otp_{phone}")
    
    return success1 and success2


def test_phone_validation():
    """Test phone number validation."""
    print_header("Test 9: Phone Number Validation")
    
    otp_service = get_otp_service()
    
    # Test invalid phone numbers
    invalid_phones = [
        ("123", "Too short"),
        ("12345678901", "Too long"),
        ("abcd123456", "Contains letters"),
        ("", "Empty"),
    ]
    
    all_rejected = True
    for phone, reason in invalid_phones:
        success, otp, message = otp_service.send_otp(phone)
        rejected = not success
        print_result(f"Reject {reason}", rejected, message)
        all_rejected = all_rejected and rejected
    
    # Test valid phone number
    success, otp, message = otp_service.send_otp("9876543210")
    print_result("Accept Valid Phone", success, f"OTP: {otp}")
    
    return all_rejected and success


def run_all_tests():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("  SMSCountry OTP System - Test Suite")
    print("🚀 "*20)
    
    tests = [
        ("OTP Generation", test_otp_generation),
        ("OTP Hashing", test_otp_hashing),
        ("OTP Storage", test_otp_storage),
        ("OTP Verification", test_otp_verification),
        ("Attempt Limiting", test_attempt_limiting),
        ("OTP Expiry", test_otp_expiry),
        ("OTP Sending", test_otp_sending),
        ("Resend Functionality", test_resend_functionality),
        ("Phone Validation", test_phone_validation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"  Success Rate: {(passed/total)*100:.1f}%")
    print(f"{'='*60}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
