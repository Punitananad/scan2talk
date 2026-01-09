#!/usr/bin/env python
"""
Script to add a missing QR code to the database.
This is useful when you have a printed QR code that's not in your local database.

Run with: python manage.py shell < fix_missing_qr.py
"""
from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway
from apps.accounts.models import User
from django.utils import timezone as django_timezone

# The QR code from your printed sticker
QR_CODE = "XSJFGZWP"

print("=" * 60)
print("FIXING MISSING QR CODE")
print("=" * 60)

# Check if it already exists
if PreGeneratedQR.objects.filter(qr_code=QR_CODE).exists():
    print(f"✅ QR code {QR_CODE} already exists!")
    qr = PreGeneratedQR.objects.get(qr_code=QR_CODE)
    print(f"   Status: {qr.status}")
    print(f"   Owner: {qr.owner}")
    print(f"   Gateway: {qr.gateway}")
else:
    print(f"❌ QR code {QR_CODE} not found. Creating it now...")
    
    # Create the QR code as available (not activated yet)
    qr = PreGeneratedQR.objects.create(
        qr_code=QR_CODE,
        status='available',
        batch_number='MANUAL-FIX',
        notes='Manually added to fix missing QR code'
    )
    
    print(f"✅ Created QR code: {qr.qr_code}")
    print(f"   Status: {qr.status}")
    print(f"   Activation URL: /gateways/activate/{qr.qr_code}/")
    print(f"   Access URL (after activation): /g/{qr.qr_code}/")
    
    print("\n📝 NEXT STEPS:")
    print("   1. Scan the QR code or visit the activation URL")
    print("   2. Complete the activation process")
    print("   3. The QR will then work normally")

print("=" * 60)
