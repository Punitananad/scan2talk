#!/usr/bin/env python
"""
Test the public gateway access URL.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.test import Client
from apps.gateways.qr_models import PreGeneratedQR

# Test QR code
qr_code = 'N9OVD7IJ'

print("\n" + "="*70)
print(f"TESTING PUBLIC URL: /g/{qr_code}/")
print("="*70)

# Check if QR exists
try:
    qr = PreGeneratedQR.objects.select_related('gateway').get(qr_code=qr_code)
    print(f"\n✅ QR Code Found:")
    print(f"   Code: {qr.qr_code}")
    print(f"   Status: {qr.status}")
    print(f"   Gateway: {qr.gateway}")
    print(f"   Gateway Active: {qr.gateway.is_active if qr.gateway else 'N/A'}")
except PreGeneratedQR.DoesNotExist:
    print(f"\n❌ QR Code '{qr_code}' not found in database")
    exit(1)

# Test the URL
print(f"\n🌐 Testing URL: /g/{qr_code}/")
client = Client()
response = client.get(f'/g/{qr_code}/')

print(f"   Response Status: {response.status_code}")

if response.status_code == 200:
    print(f"   ✅ SUCCESS: Page loaded successfully")
    print(f"   Content Type: {response.get('Content-Type', 'N/A')}")
    
    # Check if it's the correct page
    if b'gateway_access' in response.content or b'Gateway Access' in response.content:
        print(f"   ✅ Correct page: Gateway Access Form")
    elif b'gateway_not_found' in response.content or b'Gateway Not Found' in response.content:
        print(f"   ❌ ERROR: Showing 'Gateway Not Found' page")
    else:
        print(f"   ⚠️  Unknown page content")
        
elif response.status_code == 302:
    print(f"   🔄 REDIRECT to: {response.url}")
    if 'activate' in response.url:
        print(f"   ⚠️  Redirecting to activation page (QR may not be activated)")
elif response.status_code == 404:
    print(f"   ❌ ERROR: 404 Not Found")
else:
    print(f"   ❌ ERROR: Unexpected status code")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")

# Show the public URL
print(f"📱 Public URL: http://192.168.1.75:8000/g/{qr_code}/")
print(f"   Open this URL in your browser to test\n")
