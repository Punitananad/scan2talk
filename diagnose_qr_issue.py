#!/usr/bin/env python
"""
Diagnostic script to check QR code issues.
Run with: python manage.py shell < diagnose_qr_issue.py
"""
from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway

print("=" * 60)
print("QR CODE DIAGNOSTIC REPORT")
print("=" * 60)

# Check all QR codes
all_qrs = PreGeneratedQR.objects.all()
print(f"\n📊 Total QR Codes in Database: {all_qrs.count()}")

# Status breakdown
for status_code, status_name in PreGeneratedQR.STATUS_CHOICES:
    count = all_qrs.filter(status=status_code).count()
    print(f"   - {status_name}: {count}")

# Check activated QRs
print("\n✅ ACTIVATED QR CODES:")
activated_qrs = PreGeneratedQR.objects.filter(status='activated').select_related('gateway', 'owner')
if activated_qrs.exists():
    for qr in activated_qrs:
        print(f"\n   QR Code: {qr.qr_code}")
        print(f"   Owner: {qr.owner.phone if qr.owner else 'None'}")
        print(f"   Gateway: {qr.gateway.title if qr.gateway else 'None'}")
        print(f"   Gateway Active: {qr.gateway.is_active if qr.gateway else 'N/A'}")
        print(f"   Access URL: /g/{qr.qr_code}/")
        print(f"   Activated At: {qr.activated_at}")
else:
    print("   No activated QR codes found!")

# Check available QRs
print("\n📦 AVAILABLE QR CODES (Not Yet Activated):")
available_qrs = PreGeneratedQR.objects.filter(status='available')[:5]
if available_qrs.exists():
    for qr in available_qrs:
        print(f"   - {qr.qr_code} (Batch: {qr.batch_number or 'N/A'})")
else:
    print("   No available QR codes found!")

# Check for the specific QR code from the screenshot
print("\n🔍 CHECKING SPECIFIC QR CODE: XSJFGZWP")
try:
    qr = PreGeneratedQR.objects.get(qr_code='XSJFGZWP')
    print(f"   ✅ Found!")
    print(f"   Status: {qr.get_status_display()}")
    print(f"   Owner: {qr.owner}")
    print(f"   Gateway: {qr.gateway}")
except PreGeneratedQR.DoesNotExist:
    print(f"   ❌ NOT FOUND in database!")
    print(f"   This QR code does not exist in your database.")
    print(f"   Possible reasons:")
    print(f"      1. QR was never generated")
    print(f"      2. QR was deleted")
    print(f"      3. Wrong database/environment")
    print(f"      4. QR code typo")

# Check all gateways
print("\n🚪 ALL GATEWAYS:")
gateways = Gateway.objects.all()
print(f"   Total Gateways: {gateways.count()}")
for gw in gateways:
    print(f"   - {gw.title} (Active: {gw.is_active}, Owner: {gw.owner.phone if gw.owner else 'None'})")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)
print("1. If you need to use XSJFGZWP, generate it first:")
print("   - Go to admin dashboard")
print("   - Generate new QR codes")
print("   - Or use existing available QR codes")
print("\n2. To test with existing activated QRs, use:")
for qr in activated_qrs[:3]:
    print(f"   - /g/{qr.qr_code}/")
print("\n3. Make sure you're using the correct database")
print("=" * 60)
