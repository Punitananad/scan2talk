#!/usr/bin/env python
"""
Set Distributor Activation Fee to ₹1 for Testing
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.recharge_models import RechargeCategory


def set_fee_to_one():
    """Change distributor activation fee to ₹1"""
    
    print("=" * 60)
    print("SETTING DISTRIBUTOR FEE TO ₹1 FOR TESTING")
    print("=" * 60)
    
    # Get all distributor categories
    distributor_categories = RechargeCategory.objects.filter(category_type='distributor')
    
    if not distributor_categories.exists():
        print("\n❌ No distributor categories found!")
        return
    
    print(f"\n📋 Found {distributor_categories.count()} distributor categor{'y' if distributor_categories.count() == 1 else 'ies'}:")
    
    for category in distributor_categories:
        old_fee = category.distributor_activation_fee
        category.distributor_activation_fee = 1.00
        category.save()
        
        print(f"\n✅ {category.name}")
        print(f"   Old Fee: ₹{old_fee}")
        print(f"   New Fee: ₹{category.distributor_activation_fee}")
    
    print("\n" + "=" * 60)
    print("✅ DONE! Distributor fee set to ₹1")
    print("=" * 60)
    
    print("\n🧪 TESTING STEPS:")
    print("1. Scan a distributor category QR code")
    print("2. Enter distributor code: 9876543210")
    print("3. Pay ₹1 via Razorpay")
    print("4. Complete activation (phone + vehicle details)")
    print("5. Verify QR is activated and working")
    
    print("\n💡 TO RESET BACK TO ₹500:")
    print("   Run: python reset_distributor_fee_to_500.py")


if __name__ == '__main__':
    try:
        set_fee_to_one()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
