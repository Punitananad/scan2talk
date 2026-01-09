"""
Test script to verify QR activation flow fix.
Run with: python manage.py shell < test_qr_activation_flow.py
"""

from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway

print("\n" + "="*60)
print("QR ACTIVATION FLOW TEST")
print("="*60 + "\n")

# Test QR code
qr_code = "XSJFGZWP"

# Check QR status
try:
    qr = PreGeneratedQR.objects.get(qr_code=qr_code)
    
    print(f"✅ QR Code Found: {qr.qr_code}")
    print(f"   Status: {qr.status}")
    print(f"   Owner: {qr.owner}")
    print(f"   Gateway: {qr.gateway}")
    print(f"   Category: {qr.category}")
    print(f"   Access Count: {qr.access_count}")
    
    print("\n" + "-"*60)
    print("EXPECTED BEHAVIOR:")
    print("-"*60)
    
    if qr.status != 'activated':
        print(f"❌ QR is NOT activated (status: {qr.status})")
        print(f"✅ When accessing: https://scan2talk.in/gateways/g/{qr_code}/")
        print(f"   → Should REDIRECT to: https://scan2talk.in/gateways/activate/{qr_code}/")
        print(f"   → User can then activate the QR code")
    else:
        print(f"✅ QR is activated")
        if qr.gateway:
            print(f"✅ Gateway exists: {qr.gateway.id}")
            print(f"   Gateway Active: {qr.gateway.is_active}")
            print(f"   Gateway Title: {qr.gateway.title}")
            print(f"✅ When accessing: https://scan2talk.in/gateways/g/{qr_code}/")
            print(f"   → Should SHOW contact page (Call/Message buttons)")
        else:
            print(f"❌ Gateway is missing!")
            print(f"   → Should show 'Gateway Not Found' error")
    
    print("\n" + "-"*60)
    print("ACTIVATION URL:")
    print("-"*60)
    print(f"https://scan2talk.in/gateways/activate/{qr_code}/")
    
    print("\n" + "-"*60)
    print("PUBLIC ACCESS URL:")
    print("-"*60)
    print(f"https://scan2talk.in/gateways/g/{qr_code}/")
    
except PreGeneratedQR.DoesNotExist:
    print(f"❌ QR Code NOT FOUND: {qr_code}")
    print(f"   → Should show 'Gateway Not Found' error")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")

# Show all QR codes for reference
print("\n" + "="*60)
print("ALL QR CODES IN DATABASE (First 10):")
print("="*60 + "\n")

all_qrs = PreGeneratedQR.objects.all()[:10]
if all_qrs:
    for qr in all_qrs:
        status_icon = "✅" if qr.status == 'activated' else "⏳"
        gateway_info = f"Gateway: {qr.gateway.id}" if qr.gateway else "No Gateway"
        print(f"{status_icon} {qr.qr_code} - {qr.status} - {gateway_info}")
else:
    print("No QR codes found in database")

print("\n" + "="*60 + "\n")
