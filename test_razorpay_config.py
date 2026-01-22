"""
Test if Razorpay is configured correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.conf import settings
from apps.accounts.razorpay_service import RazorpayGatewayService

print("=" * 50)
print("Testing Razorpay Configuration")
print("=" * 50)

print(f"\n1. Checking settings.py:")
print(f"   RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID[:10]}..." if settings.RAZORPAY_KEY_ID else "   RAZORPAY_KEY_ID: NOT SET")
print(f"   RAZORPAY_KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:10]}..." if settings.RAZORPAY_KEY_SECRET else "   RAZORPAY_KEY_SECRET: NOT SET")
print(f"   RAZORPAY_WEBHOOK_SECRET: {settings.RAZORPAY_WEBHOOK_SECRET[:10]}..." if settings.RAZORPAY_WEBHOOK_SECRET else "   RAZORPAY_WEBHOOK_SECRET: NOT SET")

print(f"\n2. Creating Razorpay service:")
service = RazorpayGatewayService()

print(f"   Service key_id: {service.key_id[:10]}..." if service.key_id else "   Service key_id: NOT SET")
print(f"   Service key_secret: {service.key_secret[:10]}..." if service.key_secret else "   Service key_secret: NOT SET")
print(f"   Service client: {'✅ INITIALIZED' if service.client else '❌ NOT INITIALIZED'}")

if service.client:
    print("\n✅ SUCCESS: Razorpay is configured correctly!")
else:
    print("\n❌ ERROR: Razorpay client not initialized!")
    print("   Make sure your .env file has:")
    print("   RAZORPAY_KEY_ID=rzp_live_...")
    print("   RAZORPAY_KEY_SECRET=...")

print("\n" + "=" * 50)
