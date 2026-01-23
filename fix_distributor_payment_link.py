#!/usr/bin/env python
"""
Fix distributor payment links - link existing payments to distributors.
Run: python fix_distributor_payment_link.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.accounts.recharge_models import DistributorPayment

print("\n" + "="*80)
print("FIX DISTRIBUTOR PAYMENT LINKS")
print("="*80 + "\n")

# Find payments without distributor
orphan_payments = DistributorPayment.objects.filter(distributor__isnull=True)
print(f"📊 Payments without Distributor: {orphan_payments.count()}\n")

if not orphan_payments.exists():
    print("✅ All payments are already linked to distributors!")
    exit(0)

# Get all distributors
distributors = User.objects.filter(is_distributor=True, distributor_verified=True)
print(f"👥 Available Distributors: {distributors.count()}\n")

for dist in distributors:
    phone = dist.get_decrypted_phone()
    print(f"  - {dist.first_name or dist.email} ({phone})")

print(f"\n{'='*80}")
print("ORPHAN PAYMENTS:")
print(f"{'='*80}\n")

for payment in orphan_payments:
    print(f"QR Code: {payment.qr_code.qr_code}")
    print(f"Amount: ₹{payment.amount}")
    print(f"Status: {payment.status}")
    print(f"Paid At: {payment.paid_at}")
    print(f"Order ID: {payment.order_id}")
    
    # Ask user which distributor to link
    print(f"\nAvailable Distributors:")
    for i, dist in enumerate(distributors, 1):
        phone = dist.get_decrypted_phone()
        print(f"  {i}. {dist.first_name or dist.email} ({phone})")
    
    choice = input(f"\nLink to distributor (1-{distributors.count()}) or 's' to skip: ").strip()
    
    if choice.lower() == 's':
        print("Skipped.\n")
        continue
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < distributors.count():
            selected_dist = list(distributors)[idx]
            payment.distributor = selected_dist
            payment.save()
            print(f"✅ Linked to {selected_dist.first_name or selected_dist.email}\n")
        else:
            print("Invalid choice. Skipped.\n")
    except ValueError:
        print("Invalid input. Skipped.\n")
    
    print(f"{'='*60}\n")

print(f"\n{'='*80}")
print("FIX COMPLETE")
print(f"{'='*80}\n")

# Show summary
remaining_orphans = DistributorPayment.objects.filter(distributor__isnull=True).count()
linked_payments = DistributorPayment.objects.filter(distributor__isnull=False).count()

print(f"Summary:")
print(f"  - Linked Payments: {linked_payments}")
print(f"  - Orphan Payments: {remaining_orphans}")
print()
