#!/usr/bin/env python
"""
Set pricing for testing:
- Tag price: ₹499 (keep default)
- Distributor fee: ₹1 (for testing)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from apps.core.pricing_models import PricingSettings

def set_test_pricing():
    """Set pricing for testing."""
    settings = PricingSettings.get_settings()
    
    print(f"\n📊 Current Pricing:")
    print(f"   Tag Price: ₹{settings.tag_price}")
    print(f"   Distributor Fee: ₹{settings.distributor_activation_fee}")
    
    # Update distributor fee to ₹1 for testing
    settings.distributor_activation_fee = 1.00
    settings.save()
    
    print(f"\n✅ Updated Pricing:")
    print(f"   Tag Price: ₹{settings.tag_price}")
    print(f"   Distributor Fee: ₹{settings.distributor_activation_fee}")
    
    print(f"\n✨ All distributor categories have been updated automatically!")
    print(f"\n💡 To change pricing:")
    print(f"   1. Go to Admin Dashboard")
    print(f"   2. Click 'Pricing Control' button")
    print(f"   3. Update prices")
    print(f"   4. Save - all categories update automatically!")

if __name__ == '__main__':
    set_test_pricing()
