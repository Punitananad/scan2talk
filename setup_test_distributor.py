#!/usr/bin/env python
"""
Setup Test Distributor for Testing Payment Flow

Creates a test distributor with verified status for testing the payment flow.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.models import User
from django.contrib.auth.hashers import make_password


def setup_test_distributor():
    """Create a test distributor"""
    
    print("=" * 80)
    print("🔧 SETTING UP TEST DISTRIBUTOR")
    print("=" * 80)
    
    # Check if test distributor already exists
    test_phone = '9876543210'
    
    existing = User.objects.filter(username='testdist').first()
    if existing:
        print(f"\n⚠️  Test distributor already exists: {existing.username}")
        print(f"   Phone: {existing.get_decrypted_phone() if hasattr(existing, 'get_decrypted_phone') else 'N/A'}")
        print(f"   Is Distributor: {existing.is_distributor}")
        print(f"   Verified: {existing.distributor_verified}")
        
        # Update if needed
        if not existing.is_distributor or not existing.distributor_verified:
            existing.is_distributor = True
            existing.distributor_verified = True
            existing.save()
            print("\n   ✅ Updated to verified distributor status")
        
        return existing
    
    # Create new test distributor
    print("\n📝 Creating test distributor...")
    
    try:
        distributor = User.objects.create(
            username='testdist',
            email='testdist@scan2talk.in',
            first_name='Test',
            last_name='Distributor',
            phone=test_phone,
            is_distributor=True,
            distributor_verified=True,
            password=make_password('testdist123')  # Password: testdist123
        )
        
        print(f"\n✅ Test distributor created successfully!")
        print(f"\n   Username: {distributor.username}")
        print(f"   Password: testdist123")
        print(f"   Phone (Distributor Code): {test_phone}")
        print(f"   Email: {distributor.email}")
        print(f"   Is Distributor: {distributor.is_distributor}")
        print(f"   Verified: {distributor.distributor_verified}")
        
        print("\n🎯 USAGE:")
        print(f"   1. When testing payment, enter distributor code: {test_phone}")
        print(f"   2. Login to distributor dashboard:")
        print(f"      URL: http://localhost:8000/accounts/distributor/login/")
        print(f"      Username: testdist")
        print(f"      Password: testdist123")
        
        return distributor
        
    except Exception as e:
        print(f"\n❌ Error creating distributor: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    distributor = setup_test_distributor()
    
    if distributor:
        print("\n" + "=" * 80)
        print("✅ SETUP COMPLETE")
        print("=" * 80)
        print("\nYou can now test the distributor payment flow!")
        print("Run: python test_distributor_payment_flow.py")
