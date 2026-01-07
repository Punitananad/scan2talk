"""
Interactive test for Call Masking API
Run: python manage.py shell
Then paste these commands one by one
"""

# Import the service
from apps.communications.call_masking_service import create_masked_call

# Test 1: Direct function call
print("\n=== Test 1: Direct Function Call ===")
result = create_masked_call('9876543210', 'TEST-QR-001')
print(f"Success: {result['success']}")
if result['success']:
    print(f"PIN: {result['pin']}")
    print(f"Call URL: {result['call_url']}")
    print(f"Expires in: {result['expires_in_minutes']} minutes")
else:
    print(f"Error: {result['error']}")

# Test 2: With a real QR code (if you have one)
print("\n=== Test 2: With Real QR Code ===")
from apps.gateways.qr_models import PreGeneratedQR
from apps.communications.call_masking_service import create_masked_call_for_qr

# Get first activated QR code
qr = PreGeneratedQR.objects.filter(status='activated').first()
if qr:
    print(f"Testing with QR: {qr.qr_code}")
    result = create_masked_call_for_qr(qr)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"PIN: {result['pin']}")
        print(f"Call URL: {result['call_url']}")
    else:
        print(f"Error: {result['error']}")
else:
    print("No activated QR codes found. Create one first!")

# Test 3: Check PIN info
print("\n=== Test 3: Check PIN Info ===")
from apps.communications.call_masking_service import get_pin_info
if result.get('success'):
    pin = result['pin']
    info = get_pin_info(pin)
    print(f"PIN {pin} info: {info}")
else:
    print("No PIN to check")

print("\n=== Tests Complete ===\n")
