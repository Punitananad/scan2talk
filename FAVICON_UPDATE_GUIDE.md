# Favicon Update Guide

## Problem
Favicon not updating on server because browsers cache it aggressively.

## Solution Applied

### 1. Added Cache Busting
Added `?v=2` parameter to favicon URLs in `templates/base.html`:
```html
<link rel="icon" type="image/svg+xml" href="{% static 'favicon.svg' %}?v=2">
<link rel="alternate icon" href="{% static 'favicon/logo.png' %}?v=2">
<link rel="apple-touch-icon" href="{% static 'favicon/logo.png' %}?v=2">
```

## Deployment

```bash
cd /var/www/scan2talk
git pull origin main
python3 manage.py collectstatic --noinput
systemctl restart gunicorn
systemctl restart nginx
```

## Clear Browser Cache

### For Users:
1. **Chrome/Edge**: Ctrl+Shift+Delete → Clear browsing data → Cached images
2. **Firefox**: Ctrl+Shift+Delete → Cache
3. **Safari**: Cmd+Option+E
4. **Hard Refresh**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### Force Favicon Reload:
Visit directly: `https://scan2talk.in/static/favicon.svg?v=2`

### Clear Site Data (Chrome):
1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

## Verify Favicon Files Exist

```bash
# On server
ls -lh /var/www/scan2talk/static/favicon.svg
ls -lh /var/www/scan2talk/static/favicon/logo.png

# Check staticfiles
ls -lh /var/www/scan2talk/staticfiles/favicon.svg
ls -lh /var/www/scan2talk/staticfiles/favicon/logo.png
```

## Test After Deployment

1. Visit: https://scan2talk.in
2. Hard refresh: Ctrl+F5
3. Check favicon in browser tab
4. If still old, clear browser cache completely

## Future Updates

When you need to update favicon again, increment version:
- Change `?v=2` to `?v=3` in base.html
- Deploy and collect static
- Users will see new favicon immediately

## Why This Works

Browsers cache favicon.ico/svg for a LONG time (sometimes weeks). Adding `?v=2` makes the browser think it's a different file, forcing it to download the new one.
