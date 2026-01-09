#!/usr/bin/env python
"""
Fix activated QR codes that don't have gateways.
This can happen if:
1. Gateway was deleted after activation
2. Activation process failed midway
3. Database inconsistency

Run with: python manage.py shell < fix_activated_qr_without_gateway.py
"""
from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway
from django.db import transaction

print("=" * 60)
print("FIXING ACTIVATED QR CODES WITHOUT GATEWAYS")
print("=" * 60)

# Find all activated QR codes without gateways
broken_qrs = PreGeneratedQR.objects.filter(
    status='activated',
    gateway__isnull=True
).select_related('owner')

print(f"\n🔍 Found {broken_qrs.count()} activated QR codes without gateways")

if broken_qrs.count() == 0:
    print("✅ All activated QR codes have gateways!")
else:
    print("\n📋 Broken QR Codes:")
    for qr in broken_qrs:
        print(f"\n   QR Code: {qr.qr_code}")
        print(f"   Owner: {qr.owner.phone if qr.owner else 'No owner'}")
        print(f"   Owner Name: {qr.owner.full_name if qr.owner else 'N/A'}")
        print(f"   Activated: {qr.activated_at}")
        
        if qr.owner:
            # Create a gateway for this QR code
            try:
                with transaction.atomic():
                    gateway = Gateway.objects.create(
                        owner=qr.owner,
                        owner_name=qr.owner.full_name or 'Vehicle Owner',
                        title=f"Vehicle - {qr.qr_code}",
                        context_type='vehicle',
                        description='Auto-created to fix missing gateway',
                        identifier_text=qr.qr_code
                    )
                    
                    # Link gateway to QR code
                    qr.gateway = gateway
                    qr.save()
                    
                    print(f"   ✅ Created gateway: {gateway.title}")
                    print(f"   ✅ Linked to QR code")
                    
            except Exception as e:
                print(f"   ❌ Error creating gateway: {str(e)}")
        else:
            print(f"   ⚠️ Cannot create gateway - no owner!")

print("\n" + "=" * 60)
print("FIX COMPLETE")
print("=" * 60)

# Verify the fix
broken_qrs_after = PreGeneratedQR.objects.filter(
    status='activated',
    gateway__isnull=True
).count()

print(f"\n📊 Activated QR codes without gateways: {broken_qrs_after}")
if broken_qrs_after == 0:
    print("✅ All activated QR codes now have gateways!")
else:
    print(f"⚠️ Still {broken_qrs_after} QR codes without gateways")
