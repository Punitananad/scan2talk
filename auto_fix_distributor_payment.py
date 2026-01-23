#!/usr/bin/env python
"""
Automatically fix distributor payment links.
Run: python auto_fix_distributor_payment.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from apps.accounts.recharge_models import DistributorPayment

print("\n" + "="*80)
print("AUTO-FIX DISTRIBUTOR PAYMENT LINKS")
print("="*80 + "\n")

# Find payments without distributor
orphan_payments = DistributorPayment.objects.filter(distributor__isnull=True)
print(f"📊 Payments without Distributor: {orphan_payments.count()}")

if not orphan_payments.exists():
    print("✅ All payments are already linked to distributors!")
    exit(0)

# Get all distributors
distributors = User.objects.filter(is_distributor=True, distributor_verified=True)
print(f"👥 Available Distributors: {distributors.count()}\n")

if not distributors.exists():
    print("❌ No verified distributors found!")
    exit(1)

# Use the first distributor
default_dist = distributors.first()
print(f"🔗 Linking all orphan payments to: {default_dist.first_name or default_dist.email} ({default_dist.get_decrypted_phone()})\n")

fixed_count = 0
for payment in orphan_payments:
    print(f"  Fixing: QR {payment.qr_code.qr_code} - ₹{payment.amount} - {payment.status}")
    payment.distributor = default_dist
    payment.save()
    fixed_count += 1

print(f"\n✅ Fixed {fixed_count} payment(s)")

# Show summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}\n")

remaining_orphans = DistributorPayment.objects.filter(distributor__isnull=True).count()
linked_payments = DistributorPayment.objects.filter(distributor__isnull=False).count()

print(f"  - Linked Payments: {linked_payments}")
print(f"  - Orphan Payments: {remaining_orphans}")

# Show distributor stats
for dist in distributors:
    phone = dist.get_decrypted_phone()
    completed = DistributorPayment.objects.filter(distributor=dist, status='completed').count()
    total_revenue = completed * dist.distributor_commission_per_activation
    print(f"\n  Distributor: {dist.first_name or dist.email} ({phone})")
    print(f"    - Completed Payments: {completed}")
    print(f"    - Commission per Activation: ₹{dist.distributor_commission_per_activation}")
    print(f"    - Total Revenue: ₹{total_revenue}")

print()
