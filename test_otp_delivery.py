"""
Test OTP delivery with SMSCountry API - Debug version
Tests the actual SMS delivery and response parsing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.communications.otp_service import get_otp_service
import requests
import base64
from django.conf import settings

def test_direct_api_call():
    """Test direct API call to SMSCountry"""
    print("\n" + "="*60)
    print("🧪 TESTING DIRECT SMSCOUNTRY API CALL")
    print("="*60)
    
    auth_key = settings.SMSCOUNTRY_AUTH_KEY
    auth_token = settings.SMSCOUNTRY_AUTH_TOKEN
    
    print(f"\n📋 Configuration:")
    print(f"   AuthKey: {auth_key[:10]}..." if auth_key else "   AuthKey: NOT SET")
    print(f"   AuthToken: {auth_token[:10]}..." if auth_token else "   AuthToken: NOT SET")
    
    if not auth_key or not auth_token:
        print("\n❌ Credentials not configured!")
        return False
    
    # Test both endpoint formats
    endpoints = [
        f"https://restapi.smscountry.com/v0.1/Accounts/{auth_key}/SMSes/",  # Account-scoped (CORRECT)
        "https://restapi.smscountry.com/v0.1/SMSes/"  # Generic (WRONG)
    ]
    
    test_phone = "9876543210"  # Replace with your test number
    test_otp = "123456"
    
    credentials = f"{auth_key}:{auth_token}"
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_header
    }
    
    message = f"Your OTP for Scan2Talk website registration is {test_otp}. Do not share it with anyone. - Scan2Talk"
    
    payload = {
        "Text": message,
        "Number": f"91{test_phone}",
        "SenderId": "SCNTLK",
        "DLTTemplateId": "1707176830112398745",
        "Tool": "API"
    }
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {endpoint}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            print(f"\n📡 Response:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Body: {response.text}")
            
            try:
                data = response.json()
                print(f"\n📊 Parsed JSON:")
                print(f"   Success: {data.get('Success')}")
                print(f"   Message: {data.get('Message')}")
                print(f"   MessageUUID: {data.get('MessageUUID')}")
                print(f"   MessageId: {data.get('MessageId')}")
                
                if response.status_code in [200, 201, 202] and data.get("Success") is True:
                    print(f"\n✅ ENDPOINT {i} WORKS!")
                    return True
                else:
                    print(f"\n❌ ENDPOINT {i} FAILED - Success={data.get('Success')}")
            except ValueError:
                print(f"\n❌ Invalid JSON response")
                
        except Exception as e:
            print(f"\n❌ Request failed: {str(e)}")
    
    return False


def test_otp_service():
    """Test OTP service implementation"""
    print("\n" + "="*60)
    print("🧪 TESTING OTP SERVICE")
    print("="*60)
    
    otp_service = get_otp_service()
    
    print(f"\n📋 Service Configuration:")
    print(f"   API Endpoint: {otp_service.api_endpoint}")
    print(f"   Sender ID: {otp_service.SENDER_ID}")
    print(f"   DLT Template: {otp_service.DLT_TEMPLATE_ID}")
    
    test_phone = "9876543210"  # Replace with your test number
    
    print(f"\n📱 Sending OTP to: {test_phone}")
    success, otp, message = otp_service.send_otp(test_phone)
    
    print(f"\n📊 Result:")
    print(f"   Success: {success}")
    print(f"   OTP: {otp}")
    print(f"   Message: {message}")
    
    if success:
        print(f"\n✅ OTP SERVICE WORKS!")
        
        # Store and verify
        otp_service.store_otp(test_phone, otp)
        verify_success, verify_msg = otp_service.verify_otp(test_phone, otp)
        print(f"\n🔐 Verification Test:")
        print(f"   Success: {verify_success}")
        print(f"   Message: {verify_msg}")
        
        # Check delivery status
        print(f"\n📊 Checking delivery status...")
        status = otp_service.check_delivery_status(test_phone)
        if status:
            print(f"   Status: {status}")
        else:
            print(f"   Status: Not available yet")
        
        return True
    else:
        print(f"\n❌ OTP SERVICE FAILED!")
        return False


def main():
    print("\n" + "="*60)
    print("🚀 OTP DELIVERY TEST SUITE")
    print("="*60)
    
    print("\n⚠️  IMPORTANT:")
    print("   1. Update test_phone with your actual number")
    print("   2. Check .env for correct credentials")
    print("   3. Verify DLT template matches exactly")
    print("   4. Confirm sender ID is approved")
    
    input("\nPress Enter to continue...")
    
    # Test 1: Direct API call
    api_works = test_direct_api_call()
    
    # Test 2: OTP service
    service_works = test_otp_service()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"   Direct API Call: {'✅ PASS' if api_works else '❌ FAIL'}")
    print(f"   OTP Service: {'✅ PASS' if service_works else '❌ FAIL'}")
    
    if api_works and service_works:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📝 Next Steps:")
        print("   1. Check your phone for OTP SMS")
        print("   2. If not received, check SMSCountry dashboard")
        print("   3. Verify DLT template approval status")
        print("   4. Check operator delivery reports")
    else:
        print("\n❌ TESTS FAILED!")
        print("\n🔍 Troubleshooting:")
        print("   1. Verify credentials in .env")
        print("   2. Check account-scoped endpoint is used")
        print("   3. Confirm DLT template text matches exactly")
        print("   4. Verify sender ID is approved")
        print("   5. Check SMSCountry account balance")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
