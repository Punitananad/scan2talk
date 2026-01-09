# QR Code Access URL Fix

## Problem
When scanning activated QR codes, users were seeing "Gateway Not Found" error.

## Root Cause
The `get_access_url()` method in `PreGeneratedQR` model was returning the wrong URL:
- **Wrong**: `https://scan2talk.in/gateways/g/XSJFGZWP/`
- **Correct**: `https://scan2talk.in/g/XSJFGZWP/`

The extra `/gateways/` prefix was causing the URL to not match any route, resulting in a 404 error.

## Fix Applied
Updated `apps/gateways/qr_models.py` line 158:

```python
# Before
return f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/g/{self.qr_code}/"

# After
return f"{protocol}://{settings.PLATFORM_DOMAIN}/g/{self.qr_code}/"
```

## URL Structure
The correct URL structure is:

1. **Activation URL** (for new QR codes):
   - `/gateways/activate/{qr_code}/`
   - Example: `https://scan2talk.in/gateways/activate/XSJFGZWP/`

2. **Public Access URL** (for activated QR codes):
   - `/g/{qr_code}/`
   - Example: `https://scan2talk.in/g/XSJFGZWP/`

## Testing
After this fix:
1. Activated QR codes will show the correct public access URL
2. Scanning activated QR codes will work properly
3. The contact form will be displayed correctly

## Note
The QR code images themselves are correct - they point to the activation URL. This fix only affects the displayed public access URL on the QR details page and any internal redirects.
