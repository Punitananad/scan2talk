# Pricing Control - Quick Reference

## 🎯 Quick Access
**Admin Dashboard** → Click **"Pricing Control"** button (💲 amber/gold card)

Or go directly to: `/admin/core/pricingsettings/`

## 💰 Current Prices

### Tag Price: ₹499
- Physical QR tags sold on website
- Updates: Order form, payment pages

### Distributor Fee: ₹1 (Testing Mode)
- One-time activation fee for distributor QRs
- Production: ₹500
- Testing: ₹1

## 🚀 How to Change Prices

### From Admin Dashboard
```
1. Login → Admin Dashboard
2. Click "Pricing Control" (💲)
3. Update prices
4. Save
✅ Done! Updates everywhere automatically
```

### Quick Script (Testing)
```bash
python set_pricing_for_testing.py
```

## 📝 What Updates Automatically?

### When Tag Price Changes:
- ✅ Order form display
- ✅ Payment calculations
- ✅ All future orders

### When Distributor Fee Changes:
- ✅ All distributor categories
- ✅ Payment pages
- ✅ New activations

## 🔧 Quick Commands

### Check Current Prices
```python
from apps.core.pricing_models import PricingSettings
settings = PricingSettings.get_settings()
print(f"Tag: ₹{settings.tag_price}")
print(f"Distributor: ₹{settings.distributor_activation_fee}")
```

### Set Test Pricing (₹1 for distributor)
```bash
python set_pricing_for_testing.py
```

### Reset to Production
```python
from apps.core.pricing_models import PricingSettings
settings = PricingSettings.get_settings()
settings.tag_price = 499.00
settings.distributor_activation_fee = 500.00
settings.save()
```

## ⚡ Key Features
- 🎯 Single source of truth
- 🔄 Auto-updates everywhere
- 💾 Cached for performance
- 👤 User tracking
- 🔒 Staff-only access

## 🎓 Testing Flow

### Test Distributor Payment (₹1)
```
1. Run: python set_pricing_for_testing.py
2. Generate distributor QR
3. Try activation
4. Enter distributor code
5. Pay ₹1 (instead of ₹500)
6. Verify activation works ✅
```

## 📍 File Locations
- Model: `apps/core/pricing_models.py`
- Admin: `apps/core/admin.py`
- Dashboard: `templates/admin/super_dashboard.html`
- Script: `set_pricing_for_testing.py`

## 💡 Pro Tips
- Changes are instant (cached for 1 hour)
- No code deployment needed
- All changes are logged
- Can't delete pricing settings
- Only one pricing record exists

## 🆘 Troubleshooting

**Prices not updating?**
```python
from django.core.cache import cache
cache.clear()
```

**Can't access?**
- Must be staff/admin user
- URL: `/admin/core/pricingsettings/`

**Distributor categories not updating?**
```python
from apps.core.pricing_models import PricingSettings
PricingSettings.get_settings().update_distributor_categories()
```

---

**Need more details?** See `CENTRALIZED_PRICING_SYSTEM.md`
