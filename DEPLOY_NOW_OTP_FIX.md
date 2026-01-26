# 🚨 DEPLOY THIS NOW - Critical OTP Fix

## The Problem
**"OTP expired or not found"** error happens because:
- You have 3 Gunicorn workers running
- Each worker has separate memory (LocMemCache)
- Worker 1 sends OTP and stores in its memory
- Worker 2 handles verification and can't find OTP (different memory!)

## The Fix
Changed cache from **LocMemCache** (per-worker) to **FileBasedCache** (shared across all workers)

## 🚀 Deploy Commands (Run on Server)

```bash
cd /var/www/scan2talk

# 1. Create cache directory
sudo mkdir -p /var/tmp/django_cache
sudo chmod 777 /var/tmp/django_cache

# 2. Pull code
git pull origin main

# 3. Collect static
python3 manage.py collectstatic --noinput

# 4. Restart services
systemctl restart gunicorn
systemctl restart nginx

# 5. Check status
systemctl status gunicorn --no-pager
systemctl status nginx --no-pager

# 6. Test cache
python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()
from django.core.cache import cache
cache.set('test', 'works', 60)
print('✅ Cache test:', cache.get('test'))
"
```

## ✅ Expected Result
- OTP verification works on **FIRST attempt**
- No more "OTP expired or not found" errors
- Works consistently across all workers

## 🧪 Test After Deployment
1. Scan QR code
2. Enter phone number
3. Receive OTP
4. Enter OTP immediately
5. ✅ Should verify on first try!

## 📊 Monitor
```bash
# Watch cache files being created
ls -lh /var/tmp/django_cache/

# Watch OTP logs
tail -f /var/log/gunicorn/error.log | grep OTP
```

## File Changed
- `gateway_platform/settings.py` - Changed CACHES backend

This is the **ROOT CAUSE** of all OTP issues!
