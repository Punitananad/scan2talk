#!/usr/bin/env python
"""
Setup Test Distributor QR Code

Creates a test QR code with distributor category for testing.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.gateways.qr_models import PreGeneratedQR
from apps.accounts.recharge_models import RechargeCategory


def setup_test_qr():
    """Create a test distributor QR code"""
    
    print("=" * 80)
    print("🔧 SETTING UP TEST DISTRIBUTOR QR CODE")
    print("=" * 80)
    
    # Get distributor category
    dist_category = RechargeCategory.objects.filter(category_type='distributor').first()
    
    if not dist_category:
        print("\n❌ No distributor category found!")
        print("   Create one in admin first")
        return None
    
    print(f"\n✅ Using category: {dist_category.name}")
    print(f"   Activation Fee: ₹{dist_category.distributor_activation_fee}")
    
    # Check if test QR already exists
    test_code = 'TESTDIST01'
    
    existing = PreGeneratedQR.objects.filter(qr_code=test_code).first()
    if existing:
        print(f"\n⚠️  Test QR already exists: {existing.qr_code}")
        print(f"   Status: {existing.status}")
        print(f"   Category: {existing.category.name if existing.category else 'None'}")
        
        # Update category if needed
        if existing.category != dist_category:
            existing.category = dist_category
            existing.save()
            print("\n   ✅ Updated to distributor category")
        
        return existing
    
    # Create new test QR
    print(f"\n📝 Creating test QR code: {test_code}...")
    
    try:
        qr = PreGeneratedQR.objects.create(
            qr_code=test_code,
            category=dist_category,
            status='available',
            direct_service_enabled=True
        )
        
        print(f"\n✅ Test QR created successfully!")
        print(f"\n   QR Code: {qr.qr_code}")
        print(f"   Category: {qr.category.name}")
        print(f"   Status: {qr.status}")
        print(f"   Activation Fee: ₹{dist_category.distributor_activation_fee}")
        
        print("\n🎯 TESTING URLS:")
        print(f"   Payment Page:")
        print(f"   http://localhost:8000/accounts/distributor-payment/{qr.qr_code}/")
        print(f"\n   Enter distributor code: 9876543210")
        
        return qr
        
    except Exception as e:
        print(f"\n❌ Error creating QR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    qr = setup_test_qr()
    
    if qr:
        print("\n" + "=" * 80)
        print("✅ SETUP COMPLETE")
        print("=" * 80)
        print("\nYou can now test the complete flow!")
        print("Run: python test_distributor_payment_flow.py")
