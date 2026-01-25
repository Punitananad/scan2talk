# Timezone Fix - Indian Standard Time (IST)

## Problem
Dates and times were showing in UTC instead of Indian Standard Time (IST).

## Solution Applied

### 1. Updated Django Settings
**File**: `gateway_platform/settings.py`

Changed:
```python
TIME_ZONE = 'UTC'  # ❌ Before
```

To:
```python
TIME_ZONE = 'Asia/Kolkata'  # ✅ Indian Standard Time (IST)
```

### 2. Updated Dashboard Template
**File**: `templates/accounts/distributor_dashboard.html`

Added "IST" label to time display:
```html
{{ payment.paid_at|date:"h:i A" }} IST
```

## How It Works

### Django Timezone Settings
```python
TIME_ZONE = 'Asia/Kolkata'  # Sets default timezone to IST
USE_TZ = True               # Enables timezone-aware datetimes
```

With `USE_TZ = True`:
- Django stores all datetimes in UTC in the database
- Converts to `TIME_ZONE` (IST) when displaying
- IST is UTC+5:30

### Time Conversion
```
UTC Time:  2026-01-22 18:03:27
IST Time:  2026-01-23 23:33:27  (UTC + 5:30 hours)
```

## What You'll See Now

### Before (UTC)
```
Jan 22, 2026
6:03 PM
```

### After (IST)
```
Jan 23, 2026
11:33 PM IST
```

## Restart Required

After changing `TIME_ZONE` in settings.py, you need to restart the Django server:

### Development
```bash
# Stop the server (Ctrl+C)
# Then restart
python manage.py runserver
```

### Production
```bash
# Restart gunicorn/uwsgi
sudo systemctl restart gunicorn
# OR
sudo systemctl restart uwsgi
```

## Verification

### Check Current Timezone
```python
python manage.py shell

from django.utils import timezone
from django.conf import settings

print(f"TIME_ZONE: {settings.TIME_ZONE}")
print(f"Current time: {timezone.now()}")
print(f"Timezone: {timezone.get_current_timezone()}")
```

Expected output:
```
TIME_ZONE: Asia/Kolkata
Current time: 2026-01-24 23:45:00+05:30
Timezone: Asia/Kolkata
```

## Other Places Showing Dates

This fix applies to ALL dates/times in the application:

1. **Distributor Dashboard** - Commission dates ✅
2. **Admin Panel** - All timestamps
3. **User Dashboard** - Activity logs
4. **QR Activation** - Activation timestamps
5. **Payment Records** - Payment dates
6. **Logs** - System logs

## Template Date Formatting

### Common Date Filters
```django
{# Full date and time #}
{{ payment.paid_at|date:"F d, Y h:i A" }}
→ January 23, 2026 11:33 PM

{# Short date #}
{{ payment.paid_at|date:"M d, Y" }}
→ Jan 23, 2026

{# Time only #}
{{ payment.paid_at|date:"h:i A" }}
→ 11:33 PM

{# With timezone #}
{{ payment.paid_at|date:"h:i A" }} IST
→ 11:33 PM IST

{# ISO format #}
{{ payment.paid_at|date:"Y-m-d H:i:s" }}
→ 2026-01-23 23:33:27
```

## Python Code Date Formatting

### In Views
```python
from django.utils import timezone

# Get current time in IST
now = timezone.now()  # Automatically in IST

# Format for display
formatted = now.strftime("%B %d, %Y %I:%M %p IST")
# → "January 23, 2026 11:33 PM IST"
```

### In Models
```python
from django.utils import timezone as django_timezone

# Save with current IST time
payment.paid_at = django_timezone.now()
payment.save()
```

## Important Notes

1. **Database Storage**: Times are ALWAYS stored in UTC in the database
2. **Display Conversion**: Django converts to IST when displaying
3. **User Input**: When users enter times, Django assumes IST
4. **API Responses**: May need to specify timezone in API responses

## API Timezone Handling

If you have APIs, you may want to include timezone info:

```python
# In serializers
from rest_framework import serializers

class PaymentSerializer(serializers.ModelSerializer):
    paid_at_ist = serializers.SerializerMethodField()
    
    def get_paid_at_ist(self, obj):
        if obj.paid_at:
            return obj.paid_at.strftime("%Y-%m-%d %I:%M %p IST")
        return None
```

## Testing

### Test 1: Check Dashboard
1. Visit: `/accounts/distributor/dashboard/`
2. Look at "Recent Commissions" dates
3. Should show IST times with "IST" label

### Test 2: Make New Payment
1. Make a new payment
2. Check the timestamp
3. Should be in IST (5:30 hours ahead of UTC)

### Test 3: Admin Panel
1. Visit Django admin
2. Check any date/time field
3. Should show IST

## Troubleshooting

### Issue: Times Still Showing UTC
**Solution**: Restart Django server

### Issue: Times Off by 5:30 Hours
**Cause**: Server timezone vs Django timezone mismatch
**Solution**: Ensure `TIME_ZONE = 'Asia/Kolkata'` in settings

### Issue: Template Not Showing IST Label
**Cause**: Template not updated
**Solution**: Clear browser cache and refresh

## Related Settings

```python
# settings.py
LANGUAGE_CODE = 'en-us'           # English language
TIME_ZONE = 'Asia/Kolkata'        # IST timezone
USE_I18N = True                   # Enable internationalization
USE_TZ = True                     # Enable timezone support
```

## Valid Timezone Names for India

All of these work for IST:
- `Asia/Kolkata` ✅ (Recommended)
- `Asia/Calcutta` (Old name)
- `Asia/Mumbai`
- `Asia/Delhi`

All represent UTC+5:30 (Indian Standard Time)

---

**Status**: FIXED ✅  
**Date**: January 24, 2026  
**Issue**: Times showing in UTC instead of IST  
**Solution**: Changed `TIME_ZONE` to `Asia/Kolkata` and added IST label
