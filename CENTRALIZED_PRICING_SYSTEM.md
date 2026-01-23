# Centralized Pricing Control System

## Overview
A centralized system to control all pricing from one place in the admin panel. When you change prices here, they automatically update everywhere in the application.

## What Can You Control?

### 1. Physical Tag Price
- **Current Default**: ₹499
- **Used For**: Physical QR tags sold to customers on the website
- **Updates**: Order form, payment pages, calculations

### 2. Distributor Activation Fee
- **Current Default**: ₹500 (Set to ₹1 for testing)
- **Used For**: One-time payment for distributor category QR codes
- **Updates**: Distributor payment pages, all distributor categories

## How to Use

### Method 1: Admin Dashboard (Recommended)
1. Login to admin panel
2. Go to **Admin Dashboard**
3. Click the **"Pricing Control"** button (💲 icon, amber/gold colored)
4. Update the prices:
   - **Tag price**: Price for physical QR tags
   - **Distributor activation fee**: One-time fee for distributor QRs
5. Click **Save**
6. ✅ All prices update automatically everywhere!

### Method 2: Django Admin
1. Go to `/admin/`
2. Navigate to **Core** → **Pricing Settings**
3. Update prices
4. Save

### Method 3: Python Script (For Testing)
```bash
python set_pricing_for_testing.py
```

## What Happens When You Change Prices?

### Tag Price Changes
When you update the tag price:
- ✅ Order form shows new price
- ✅ Payment calculations use new price
- ✅ All future orders use new price
- ❌ Existing orders are NOT affected (they keep their original price)

### Distributor Fee Changes
When you update the distributor activation fee:
- ✅ All distributor categories update automatically
- ✅ New distributor payments use new fee
- ✅ Payment pages show new fee
- ❌ Completed payments are NOT affected

## Technical Details

### Database Model
- **Table**: `pricing_settings`
- **Location**: `apps/core/pricing_models.py`
- **Type**: Single instance model (only one record exists)

### Key Features
1. **Single Source of Truth**: Only one pricing record exists
2. **Automatic Updates**: Changes propagate to all distributor categories
3. **Caching**: Prices are cached for 1 hour for performance
4. **User Tracking**: Records who made the last change
5. **Validation**: Prevents multiple pricing records

### Files Modified
```
apps/core/pricing_models.py          # Pricing model
apps/core/models.py                  # Import pricing model
apps/core/admin.py                   # Admin interface (NEW)
apps/core/views.py                   # Use dynamic pricing
apps/accounts/wallet_views.py        # Use dynamic pricing
templates/core/order_tag.html        # Display dynamic price
templates/admin/super_dashboard.html # Pricing control button
```

### Migration
```bash
python manage.py makemigrations core
python manage.py migrate
```

## Testing

### Test Distributor Payment with ₹1 Fee
```bash
# Set fee to ₹1
python set_pricing_for_testing.py

# Test the flow:
1. Generate a distributor category QR
2. Try to activate it
3. Enter distributor code
4. Pay ₹1 (instead of ₹500)
5. Verify activation works
```

### Reset to Production Pricing
```python
from apps.core.pricing_models import PricingSettings

settings = PricingSettings.get_settings()
settings.tag_price = 499.00
settings.distributor_activation_fee = 500.00
settings.save()
```

## API Usage

### Get Current Prices
```python
from apps.core.pricing_models import PricingSettings

# Get tag price
tag_price = PricingSettings.get_tag_price()

# Get distributor fee
distributor_fee = PricingSettings.get_distributor_fee()

# Get full settings object
settings = PricingSettings.get_settings()
```

### Update Prices
```python
from apps.core.pricing_models import PricingSettings

settings = PricingSettings.get_settings()
settings.tag_price = 599.00
settings.distributor_activation_fee = 1.00
settings.save()  # Automatically updates all distributor categories
```

## Benefits

### Before (Hardcoded Prices)
- ❌ Prices scattered across multiple files
- ❌ Need to edit code to change prices
- ❌ Risk of missing some locations
- ❌ Requires code deployment to change prices
- ❌ No audit trail

### After (Centralized System)
- ✅ Single source of truth
- ✅ Change prices from admin panel
- ✅ Automatic propagation everywhere
- ✅ No code changes needed
- ✅ User tracking and audit trail
- ✅ Cached for performance

## Security

### Permissions
- Only **staff users** can access pricing settings
- Only **superusers** can modify prices in Django admin
- Changes are logged with user information

### Validation
- Cannot create multiple pricing records
- Cannot delete the pricing settings
- Prices must be positive numbers

## Troubleshooting

### Prices Not Updating?
1. Clear cache: `python manage.py shell` → `from django.core.cache import cache` → `cache.clear()`
2. Restart server
3. Check if pricing settings exist: `PricingSettings.objects.exists()`

### Distributor Categories Not Updating?
The `save()` method automatically updates all distributor categories. If not working:
```python
from apps.core.pricing_models import PricingSettings
settings = PricingSettings.get_settings()
settings.update_distributor_categories()  # Manual update
```

### Can't Access Pricing Control?
- Make sure you're logged in as staff/admin
- URL: `/admin/core/pricingsettings/`
- Or use the button on Admin Dashboard

## Future Enhancements

Possible additions:
- Bulk discount tiers (10+ tags = 10% off)
- Seasonal pricing
- Promotional codes
- Regional pricing
- Currency support
- Price history tracking
- Scheduled price changes

## Summary

You now have complete control over pricing from one place:
1. **Tag Price**: ₹499 (for physical QR tags)
2. **Distributor Fee**: ₹1 (for testing, normally ₹500)

Change them anytime from the admin panel, and they update everywhere automatically! 🎉
