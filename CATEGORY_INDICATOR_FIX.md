# Category Indicator Fix

## Issue
Category indicators were not showing in the batch preview because the `category` field was not being passed to the template.

## Fix Applied
Updated `apps/gateways/qr_download_views.py` in the `preview_batch_sample` function:

### Before
```python
qr_data_list.append({
    'qr_code': qr.qr_code,
    'qr_code_data': generate_qr_base64(qr.qr_code)
})
```

### After
```python
qr_data_list.append({
    'qr_code': qr.qr_code,
    'qr_code_data': generate_qr_base64(qr.qr_code),
    'category': qr.category  # Include category for visual indicator
})
```

Also added `.select_related('category')` to optimize the database query.

## How to Test

1. **Refresh the preview page** (Ctrl+F5 or Cmd+Shift+R)
2. You should now see colored corner badges:
   - 🟢 Green "F" for Free
   - 🔵 Blue "P" for Prepaid
   - 🟣 Purple "PP" for Postpaid
   - 🟠 Amber "T" for Trial
   - 🔴 Red "D" for Distributor

## What You'll See

```
┌─────────────────────────┐
│ SCAN2TALK          🔴D  │ ← Red triangle with "D"
│                         │
│  SCAN TO CONTACT        │
│  VEHICLE OWNER   [QR]   │
│                  ABC123 │
└─────────────────────────┘
```

## If Still Not Showing

1. **Hard refresh** the page (Ctrl+Shift+R)
2. **Clear browser cache**
3. **Check browser console** for any errors
4. **Verify QR codes have category assigned** in admin panel

## Status
✅ Fixed - Category indicators will now appear in batch preview and when printing
