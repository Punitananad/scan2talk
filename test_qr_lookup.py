"""
Quick test script to check QR code in database.
Run with: python manage.py shell < test_qr_lookup.py
"""

from apps.gateways.qr_models import PreGeneratedQR

qr_code = "XSJFGZWP"

print(f"\n=== Testing QR Code: {qr_code} ===\n")

# Test 1: Check if QR exists
try:
    qr = PreGeneratedQR.objects.get(qr_code=qr_code)
    print(f"✅ QR Code found: {qr.qr_code}")
    print(f"   Status: {qr.status}")
    print(f"   Owner: {qr.owner}")
    print(f"   Gateway: {qr.gateway}")
    if qr.gateway:
        print(f"   Gateway ID: {qr.gateway.id}")
        print(f"   Gateway Active: {qr.gateway.is_active}")
        print(f"   Gateway Title: {qr.gateway.title}")
    print(f"   Category: {qr.category}")
except PreGeneratedQR.DoesNotExist:
    print(f"❌ QR Code NOT FOUND: {qr_code}")
    
# Test 2: List all QR codes
print(f"\n=== All QR Codes ===\n")
all_qrs = PreGeneratedQR.objects.all()[:10]
for qr in all_qrs:
    print(f"  {qr.qr_code} - {qr.status} - Gateway: {qr.gateway}")

print("\n=== Test Complete ===\n")
