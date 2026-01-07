"""
Test script for SparkTG Call Masking API integration.
Run with: python manage.py shell < test_call_masking.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.communications.call_masking_service import create_masked_call

# Test the service
print("\n" + "="*60)
print("Testing SparkTG Call Masking API Integration")
print("="*60 + "\n")

# Test with sample data
test_phone = "9876543210"
test_qr_id = "TEST-QR-001"

print(f"Creating masked call for:")
print(f"  Phone: {test_phone}")
print(f"  QR ID: {test_qr_id}")
print("\nCalling API...\n")

result = create_masked_call(test_phone, test_qr_id)

print("Result:")
print("-" * 60)
if result['success']:
    print(f"✓ Success!")
    print(f"  PIN: {result['pin']}")
    print(f"  Call URL: {result['call_url']}")
    print(f"  DID Number: {result['did_number']}")
    print(f"  Expires in: {result['expires_in_minutes']} minutes")
    print(f"\nUser can click: {result['call_url']}")
    print(f"Or dial: {result['did_number']} and enter PIN: {result['pin']}")
else:
    print(f"✗ Failed!")
    print(f"  Error: {result.get('error', 'Unknown error')}")
    if 'details' in result:
        print(f"  Details: {result['details']}")

print("\n" + "="*60 + "\n")
