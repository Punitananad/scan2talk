#!/usr/bin/env python
"""
Test SMSCountry API connection and OTP sending.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.communications.otp_service import get_otp_service
import requests
import base64
from django.conf import settings

def test_credentials():
    """Test if credentials are loaded."""
    print("="*60)
    print("STEP 1: Testing Credentials")
    print("="*60)
    
    auth_key = settings.SMSCOUNTRY_AUTH_KEY
    auth_token = settings.SMSCOUNTRY_AUTH_TOKEN
    
    print(f"AuthKey: {auth_key[:10]}... (length: {len(auth_key)})")
    print(f"AuthToken: {auth_token[:10]}... (length: {len(auth_token)})")
    
    if not auth_key or not auth_token:
        print("❌ ERROR: Credentials not configured!")
        return False
    
    print("✅ Credentials loaded")
    return True

def test_api_connection():
    """Test direct API connection."""
    print("\n" + "="*60)
    print("STEP 2: Testing API Connection")
    print("="*60)
    
    auth_key = settings.SMSCOUNTRY_AUTH_KEY
    auth_token = settings.SMSCOUNTRY_AUTH_TOKEN
    
    # Create auth header
    credentials = f"{auth_key}:{auth_token}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded}"
    }
    
    # Test payload
    payload = {
        "Text": "Test message from Scan2Talk",
        "Number": "919876543210",  # Test number
        "SenderId": "SCNTLK",
        "DLTTemplateId": "1707176830112398745",
        "Tool": "API"
    }
    
    print(f"Endpoint: https://restapi.smscountry.com/v0.1/SMSes/")
    print(f"Sender ID: SCNTLK")
    print(f"DLT Template: 1707176830112398745")
    
    try:
        response = requests.post(
            "https://restapi.smscountry.com/v0.1/SMSes/",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code in [200, 201, 202]:
            print("✅ API connection successful!")
            return True
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"Error details: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_otp_service():
    """Test OTP service."""
    print("\n" + "="*60)
    print("STEP 3: Testing OTP Service")
    print("="*60)
    
    otp_service = get_otp_service()
    
    # Test with a phone number
    test_phone = "9876543210"
    print(f"Testing with phone: {test_phone}")
    
    success, otp, message = otp_service.send_otp(test_phone)
    
    print(f"\nResult: {'✅ Success' if success else '❌ Failed'}")
    print(f"OTP: {otp}")
    print(f"Message: {message}")
    
    return success

def main():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("  SMSCountry API Test Suite")
    print("🚀 "*20 + "\n")
    
    # Test 1: Credentials
    if not test_credentials():
        print("\n❌ FAILED: Credentials not configured")
        print("\nPlease add to .env:")
        print("SMSCOUNTRY_AUTH_KEY=your_auth_key")
        print("SMSCOUNTRY_AUTH_TOKEN=your_auth_token")
        return
    
    # Test 2: API Connection
    api_works = test_api_connection()
    
    # Test 3: OTP Service
    otp_works = test_otp_service()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Credentials: ✅")
    print(f"API Connection: {'✅' if api_works else '❌'}")
    print(f"OTP Service: {'✅' if otp_works else '❌'}")
    
    if api_works and otp_works:
        print("\n✅ All tests passed! SMS should be working.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("1. Invalid credentials")
        print("2. DLT template not approved")
        print("3. Sender ID not approved")
        print("4. Insufficient balance in SMSCountry account")
        print("5. Network connectivity issues")

if __name__ == "__main__":
    main()
