"""
Quick OTP Production Diagnostic
Run this on production server to see what's happening
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.conf import settings
import requests
import base64

print("\n" + "="*70)
print("🔍 OTP PRODUCTION DIAGNOSTIC")
print("="*70)

# Check 1: Credentials
print("\n1️⃣  CHECKING CREDENTIALS")
print("-" * 70)
auth_key = getattr(settings, 'SMSCOUNTRY_AUTH_KEY', None)
auth_token = getattr(settings, 'SMSCOUNTRY_AUTH_TOKEN', None)

if auth_key:
    print(f"✅ AuthKey: {auth_key[:15]}...{auth_key[-5:]}")
else:
    print("❌ AuthKey: NOT SET")

if auth_token:
    print(f"✅ AuthToken: {auth_token[:15]}...{auth_token[-5:]}")
else:
    print("❌ AuthToken: NOT SET")

if not auth_key or not auth_token:
    print("\n❌ STOP: Credentials not configured!")
    sys.exit(1)

# Check 2: Endpoint
print("\n2️⃣  CHECKING ENDPOINT")
print("-" * 70)
endpoint = f"https://restapi.smscountry.com/v0.1/Accounts/{auth_key}/SMSes/"
print(f"Endpoint: {endpoint}")

# Check 3: Test API Call
print("\n3️⃣  TESTING API CALL")
print("-" * 70)

test_phone = input("Enter test phone number (10 digits): ").strip()
if len(test_phone) != 10:
    print("❌ Invalid phone number")
    sys.exit(1)

credentials = f"{auth_key}:{auth_token}"
auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"

headers = {
    "Content-Type": "application/json",
    "Authorization": auth_header
}

# Use EXACT DLT template
message = "Your OTP for Scan2Talk website registration is 123456. Do not share it with anyone. - Scan2Talk"

payload = {
    "Text": message,
    "Number": f"91{test_phone}",
    "SenderId": "SCNTLK",
    "DLTTemplateId": "1707176830112398745",
    "Tool": "API"
}

print(f"\n📤 Sending request to: {endpoint}")
print(f"📱 Phone: 91{test_phone}")
print(f"📝 Message: {message[:50]}...")

try:
    response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
    
    print(f"\n📥 RESPONSE:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nBody:")
    print(response.text)
    
    # Parse JSON
    try:
        data = response.json()
        print(f"\n📊 PARSED:")
        for key, value in data.items():
            print(f"   {key}: {value}")
        
        # Check success
        if data.get("Success") is True:
            print(f"\n✅ SUCCESS! Message sent")
            print(f"MessageID: {data.get('MessageUUID') or data.get('MessageId')}")
            print(f"\n📱 Check phone {test_phone} for OTP: 123456")
        else:
            print(f"\n❌ FAILED!")
            print(f"Error: {data.get('Message') or data.get('Error')}")
            
            # Common issues
            print(f"\n🔍 TROUBLESHOOTING:")
            error_msg = str(data.get('Message', '')).lower()
            
            if 'dlt' in error_msg or 'template' in error_msg:
                print("   ⚠️  DLT Template Issue:")
                print("      - Login to DLT portal")
                print("      - Verify template ID: 1707176830112398745")
                print("      - Check template is approved")
                print("      - Confirm text matches EXACTLY")
            
            if 'sender' in error_msg:
                print("   ⚠️  Sender ID Issue:")
                print("      - Verify SCNTLK is approved")
                print("      - Check sender ID in DLT portal")
            
            if 'balance' in error_msg or 'credit' in error_msg:
                print("   ⚠️  Balance Issue:")
                print("      - Check SMSCountry account balance")
                print("      - Recharge if needed")
            
            if 'invalid' in error_msg and 'number' in error_msg:
                print("   ⚠️  Phone Number Issue:")
                print("      - Try different format")
                print("      - Check if number is DND")
    
    except ValueError:
        print(f"\n❌ Invalid JSON response")
        print("Raw response:", response.text)

except requests.exceptions.Timeout:
    print(f"\n❌ REQUEST TIMEOUT")
    print("   - Check internet connection")
    print("   - Verify API endpoint is accessible")

except requests.exceptions.RequestException as e:
    print(f"\n❌ REQUEST FAILED: {str(e)}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

# Check 4: OTP Service
print("\n" + "="*70)
print("4️⃣  CHECKING OTP SERVICE")
print("-" * 70)

from apps.communications.otp_service import get_otp_service

otp_service = get_otp_service()
print(f"API Endpoint: {otp_service.api_endpoint}")
print(f"Sender ID: {otp_service.SENDER_ID}")
print(f"DLT Template: {otp_service.DLT_TEMPLATE_ID}")

print("\n" + "="*70)
print("✅ DIAGNOSTIC COMPLETE")
print("="*70)
