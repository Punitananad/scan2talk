#!/usr/bin/env python
"""
Debug script to check distributor commission tracking.
Run: python debug_distributor_commission.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.accounts.recharge_models import DistributorPayment
from apps.gateways.qr_models import PreGeneratedQR

print("\n" + "="*80)
print("DISTRIBUTOR COMMISSION DEBUG")
print("="*80 + "\n")

# Find all distributors
distributors = User.objects.filter(is_distributor=True, distributor_verified=True)
print(f"📊 Total Verified Distributors: {distributors.count()}\n")

for dist in distributors:
    phone = dist.get_decrypted_phone()
    print(f"\n{'='*60}")
    print(f"👤 Distributor: {dist.first_name or dist.email}")
    print(f"   Phone: {phone}")
    print(f"   Email: {dist.email}")
    print(f"   Total QR Assigned: {dist.distributor_total_qr}")
    print(f"   Commission per Activation: ₹{dist.distributor_commission_per_activation}")
    print(f"{'='*60}")
    
    # Check DistributorPayment records
    payments = DistributorPayment.objects.filter(distributor=dist)
    print(f"\n💰 DistributorPayment Records:")
    print(f"   Total: {payments.count()}")
    print(f"   Pending: {payments.filter(status='pending').count()}")
    print(f"   Completed: {payments.filter(status='completed').count()}")
    print(f"   Failed: {payments.filter(status='failed').count()}")
    
    # Show completed payments
    completed = payments.filter(status='completed')
    if completed.exists():
        print(f"\n   ✅ Completed Payments:")
        for payment in completed:
            print(f"      - QR: {payment.qr_code.qr_code}")
            print(f"        Amount: ₹{payment.amount}")
            print(f"        Paid At: {payment.paid_at}")
            print(f"        Order ID: {payment.order_id}")
            print()
    else:
        print(f"   ❌ No completed payments found!")
    
    # Check QR codes linked to this distributor via payments
    qr_codes_with_payment = PreGeneratedQR.objects.filter(
        distributor_payment__distributor=dist
    ).distinct()
    print(f"\n📱 QR Codes Linked via Payment:")
    print(f"   Total: {qr_codes_with_payment.count()}")
    print(f"   Activated: {qr_codes_with_payment.filter(status='activated').count()}")
    print(f"   Available: {qr_codes_with_payment.filter(status='available').count()}")
    
    # Check if any QR codes have payments
    qr_with_payments = PreGeneratedQR.objects.filter(
        distributor_payment__isnull=False,
        distributor_payment__distributor=dist
    )
    print(f"\n💳 QR Codes with Payment Records:")
    print(f"   Total: {qr_with_payments.count()}")
    
    if qr_with_payments.exists():
        for qr in qr_with_payments:
            try:
                payment = qr.distributor_payment
                print(f"      - QR: {qr.qr_code}")
                print(f"        Status: {payment.status}")
                print(f"        Amount: ₹{payment.amount}")
                if payment.paid_at:
                    print(f"        Paid At: {payment.paid_at}")
                print()
            except:
                pass

# Check all DistributorPayment records
print(f"\n{'='*80}")
print("ALL DISTRIBUTOR PAYMENTS IN SYSTEM")
print(f"{'='*80}\n")

all_payments = DistributorPayment.objects.all()
print(f"Total DistributorPayment Records: {all_payments.count()}")
print(f"  - Pending: {all_payments.filter(status='pending').count()}")
print(f"  - Completed: {all_payments.filter(status='completed').count()}")
print(f"  - Failed: {all_payments.filter(status='failed').count()}")

if all_payments.exists():
    print(f"\nRecent Payments:")
    for payment in all_payments.order_by('-created_at')[:10]:
        print(f"\n  QR Code: {payment.qr_code.qr_code}")
        print(f"  Status: {payment.status}")
        print(f"  Amount: ₹{payment.amount}")
        print(f"  Distributor: {payment.distributor.email if payment.distributor else 'None'}")
        if payment.paid_at:
            print(f"  Paid At: {payment.paid_at}")
        print(f"  Created: {payment.created_at}")

print(f"\n{'='*80}")
print("DIAGNOSIS COMPLETE")
print(f"{'='*80}\n")
