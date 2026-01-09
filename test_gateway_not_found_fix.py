#!/usr/bin/env python
"""
Test script to verify the "Gateway Not Found" bug fix.

This script tests that:
1. Activated QR codes ALWAYS work, even if gateway.is_active=False
2. The gateway is automatically reactivated when accessed
3. No "Gateway Not Found" errors occur for valid activated QRs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.gateways.qr_models import PreGeneratedQR
from apps.gateways.models import Gateway
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()


def test_gateway_not_found_bug():
    """Test the gateway not found bug fix."""
    print("\n" + "="*70)
    print("TESTING: Gateway Not Found Bug Fix")
    print("="*70)
    
    # Find an activated QR code
    activated_qrs = PreGeneratedQR.objects.filter(
        status='activated',
        gateway__isnull=False
    ).select_related('gateway')
    
    if not activated_qrs.exists():
        print("❌ No activated QR codes found. Please activate a QR first.")
        return
    
    qr = activated_qrs.first()
    gateway = qr.gateway
    
    print(f"\n📋 Test Setup:")
    print(f"   QR Code: {qr.qr_code}")
    print(f"   Gateway ID: {gateway.id}")
    print(f"   Gateway Title: {gateway.title}")
    print(f"   Gateway is_active: {gateway.is_active}")
    
    # Test 1: Deactivate the gateway (simulate the bug condition)
    print(f"\n🔧 Test 1: Simulating bug condition...")
    print(f"   Setting gateway.is_active = False")
    gateway.is_active = False
    gateway.save(update_fields=['is_active'])
    
    # Verify it's deactivated
    gateway.refresh_from_db()
    print(f"   ✓ Gateway is now inactive: {not gateway.is_active}")
    
    # Test 2: Try to access the QR URL (GET request)
    print(f"\n🌐 Test 2: Accessing QR URL (GET request)...")
    client = Client()
    url = f'/g/{qr.qr_code}/'
    print(f"   URL: {url}")
    
    response = client.get(url)
    print(f"   Response status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ SUCCESS: Page loaded successfully")
        
        # Check if gateway was reactivated
        gateway.refresh_from_db()
        if gateway.is_active:
            print(f"   ✅ Gateway was automatically reactivated!")
        else:
            print(f"   ⚠️  WARNING: Gateway is still inactive")
    else:
        print(f"   ❌ FAILED: Got status {response.status_code}")
        if b'Gateway Not Found' in response.content or b'gateway_not_found' in response.content:
            print(f"   ❌ ERROR: 'Gateway Not Found' page was shown!")
    
    # Test 3: Try POST request (form submission)
    print(f"\n📤 Test 3: Testing POST request (form submission)...")
    
    # First, ensure gateway is inactive again
    gateway.is_active = False
    gateway.save(update_fields=['is_active'])
    gateway.refresh_from_db()
    print(f"   Gateway is_active before POST: {gateway.is_active}")
    
    # Try to submit a message
    post_data = {
        'channel': 'sms',
        'message': 'Test message to verify bug fix',
        'intent': 'general'
    }
    
    response = client.post(url, data=post_data)
    print(f"   Response status: {response.status_code}")
    
    if response.status_code in [200, 302]:  # 200 or redirect
        print(f"   ✅ SUCCESS: POST request processed")
        
        # Check if gateway was reactivated
        gateway.refresh_from_db()
        if gateway.is_active:
            print(f"   ✅ Gateway was automatically reactivated on POST!")
        else:
            print(f"   ⚠️  WARNING: Gateway is still inactive after POST")
    else:
        print(f"   ❌ FAILED: Got status {response.status_code}")
    
    # Test 4: Verify QR status is still 'activated'
    print(f"\n🔍 Test 4: Verifying QR status...")
    qr.refresh_from_db()
    print(f"   QR status: {qr.status}")
    
    if qr.status == 'activated':
        print(f"   ✅ QR status is still 'activated' (correct)")
    else:
        print(f"   ❌ ERROR: QR status changed to '{qr.status}'")
    
    # Final summary
    print(f"\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    gateway.refresh_from_db()
    print(f"Final gateway.is_active: {gateway.is_active}")
    print(f"Final QR status: {qr.status}")
    
    if gateway.is_active and qr.status == 'activated':
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"   The bug is fixed. Activated QRs now work even if gateway was inactive.")
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED")
        print(f"   Please review the test results above.")
    
    print("="*70 + "\n")


if __name__ == '__main__':
    test_gateway_not_found_bug()
