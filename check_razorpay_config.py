#!/usr/bin/env python
"""
Diagnostic script to check Razorpay configuration on production server.
Run this on your production server to verify Razorpay credentials are loaded.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.conf import settings
from apps.accounts.razorpay_service import RazorpayGatewayService

print("=" * 60)
print("RAZORPAY CONFIGURATION CHECK")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   RAZORPAY_KEY_ID: {'✓ SET' if os.getenv('RAZORPAY_KEY_ID') else '✗ NOT SET'}")
print(f"   RAZORPAY_KEY_SECRET: {'✓ SET' if os.getenv('RAZORPAY_KEY_SECRET') else '✗ NOT SET'}")
print(f"   RAZORPAY_WEBHOOK_SECRET: {'✓ SET' if os.getenv('RAZORPAY_WEBHOOK_SECRET') else '✗ NOT SET'}")

# Check Django settings
print("\n2. Django Settings:")
key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')

print(f"   RAZORPAY_KEY_ID: {'✓ ' + key_id[:10] + '...' if key_id else '✗ EMPTY'}")
print(f"   RAZORPAY_KEY_SECRET: {'✓ SET (hidden)' if key_secret else '✗ EMPTY'}")
print(f"   RAZORPAY_WEBHOOK_SECRET: {'✓ SET (hidden)' if webhook_secret else '✗ EMPTY'}")

# Check Razorpay service initialization
print("\n3. Razorpay Service:")
service = RazorpayGatewayService()
if service.client:
    print("   ✓ Razorpay client initialized successfully")
    print(f"   ✓ Key ID: {service.key_id[:10]}...")
else:
    print("   ✗ Razorpay client NOT initialized")
    print("   ✗ Credentials missing or invalid")

# Check .env file
print("\n4. .env File Check:")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"   ✓ .env file exists at: {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'RAZORPAY_KEY_ID' in content:
            print("   ✓ RAZORPAY_KEY_ID found in .env")
        else:
            print("   ✗ RAZORPAY_KEY_ID NOT found in .env")
        
        if 'RAZORPAY_KEY_SECRET' in content:
            print("   ✓ RAZORPAY_KEY_SECRET found in .env")
        else:
            print("   ✗ RAZORPAY_KEY_SECRET NOT found in .env")
else:
    print(f"   ✗ .env file NOT found at: {env_path}")

print("\n" + "=" * 60)
print("DIAGNOSIS:")
print("=" * 60)

if service.client:
    print("✓ Razorpay is properly configured!")
    print("  Payment gateway should work correctly.")
else:
    print("✗ Razorpay is NOT configured!")
    print("\nPossible issues:")
    print("1. .env file not loaded on production server")
    print("2. Environment variables not set in production")
    print("3. Credentials are empty or invalid")
    print("\nSolutions:")
    print("1. Ensure .env file exists on production server")
    print("2. Restart your Django application after adding credentials")
    print("3. Check if python-dotenv is installed: pip install python-dotenv")
    print("4. Verify settings.py loads .env file correctly")

print("=" * 60)
