#!/usr/bin/env python
"""
Check Django timezone configuration.
Run: python check_timezone.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from apps.accounts.recharge_models import DistributorPayment

print("\n" + "="*80)
print("TIMEZONE CONFIGURATION CHECK")
print("="*80 + "\n")

# Check settings
print(f"📍 TIME_ZONE Setting: {settings.TIME_ZONE}")
print(f"🌍 USE_TZ: {settings.USE_TZ}")
print(f"🕐 Current Timezone: {timezone.get_current_timezone()}")
print(f"⏰ Current Time: {timezone.now()}")
print(f"📅 Formatted: {timezone.now().strftime('%B %d, %Y %I:%M %p %Z')}")

# Check a payment record
print(f"\n{'='*80}")
print("SAMPLE PAYMENT TIMESTAMP")
print(f"{'='*80}\n")

payment = DistributorPayment.objects.filter(paid_at__isnull=False).first()
if payment:
    print(f"Payment QR: {payment.qr_code.qr_code}")
    print(f"Paid At (raw): {payment.paid_at}")
    print(f"Paid At (formatted): {payment.paid_at.strftime('%B %d, %Y %I:%M %p IST')}")
    print(f"Timezone: {payment.paid_at.tzinfo}")
else:
    print("No payments found with paid_at timestamp")

print(f"\n{'='*80}")
print("TIMEZONE INFO")
print(f"{'='*80}\n")

import pytz
ist = pytz.timezone('Asia/Kolkata')
utc = pytz.UTC

now_utc = timezone.now().astimezone(utc)
now_ist = timezone.now().astimezone(ist)

print(f"UTC Time:  {now_utc.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
print(f"IST Time:  {now_ist.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
print(f"Difference: +5:30 hours")

print(f"\n{'='*80}")
print("✅ TIMEZONE CHECK COMPLETE")
print(f"{'='*80}\n")
