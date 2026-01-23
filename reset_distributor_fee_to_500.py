#!/usr/bin/env python
"""
Reset Distributor Activation Fee back to ₹500
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.accounts.recharge_models import RechargeCategory


def reset_fee_to_500():
    """Reset distributor activation fee to ₹500"""
    
    print("=" * 60)
    print("RESETTING DISTRIBUTOR FEE TO ₹500")
    print("=" * 60)
    
    # Get all distributor categories
    distributor_categories = RechargeCategory.objects.filter(category_type='distributor')
    
    if not distributor_categories.exists():
        print("\n❌ No distributor categories found!")
        return
    
    print(f"\n📋 Found {distributor_categories.count()} distributor categor{'y' if distributor_categories.count() == 1 else 'ies'}:")
    
    for category in distributor_categories:
        old_fee = category.distributor_activation_fee
        category.distributor_activation_fee = 500.00
        category.save()
        
        print(f"\n✅ {category.name}")
        print(f"   Old Fee: ₹{old_fee}")
        print(f"   New Fee: ₹{category.distributor_activation_fee}")
    
    print("\n" + "=" * 60)
    print("✅ DONE! Distributor fee reset to ₹500")
    print("=" * 60)


if __name__ == '__main__':
    try:
        reset_fee_to_500()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
