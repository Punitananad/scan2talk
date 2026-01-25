# Clear Browser Cache - See Updated Page

## Problem
The page is still showing the old version with both "Call Owner" and "Send Message" buttons, even though the code has been updated to show only "Call Owner".

## Cause
Your browser has cached the old HTML/CSS/JavaScript files.

## Solution

### Option 1: Hard Refresh (Quickest)
**Windows/Linux**: Press `Ctrl + F5` or `Ctrl + Shift + R`  
**Mac**: Press `Cmd + Shift + R`

This forces the browser to reload all files from the server, bypassing the cache.

### Option 2: Clear Browser Cache (Chrome)
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "Cached images and files"
3. Time range: "Last hour" or "All time"
4. Click "Clear data"
5. Refresh the page (F5)

### Option 3: Open in Incognito/Private Mode
1. Press `Ctrl + Shift + N` (Chrome) or `Ctrl + Shift + P` (Firefox)
2. Visit the page: `http://scan2talk.in/g/LLRBIUR3/`
3. Should show only "Call Owner" button

### Option 4: Restart Django Server
If hard refresh doesn't work:

```bash
# Stop the server (Ctrl+C)
# Then restart
python manage.py runserver
```

## Verification

After clearing cache, you should see:

### ✅ Correct (After Cache Clear)
```
┌──────────────────────────────┐
│                              │
│      📞 Call Owner           │
│  Make an anonymous call      │
│  Your number stays private   │
│                              │
└──────────────────────────────┘
```

### ❌ Old (Cached Version)
```
┌─────────────────────────────────────┐
│  📞 Call Owner  │  💬 Send Message  │
└─────────────────────────────────────┘
```

## Quick Test

1. Press `Ctrl + F5` to hard refresh
2. Check if "Send Message" button is gone
3. Should only see green "Call Owner" button

## If Still Not Working

### Check File Was Updated
The file `templates/core/gateway_access.html` should have:
- Line 61: `<div class="flex justify-center mb-8">` (not `grid grid-cols-1 md:grid-cols-2`)
- Only ONE button (Call Owner)
- No "Send Message" button

### Verify Server is Running
```bash
# Check if server is running
# Should see: "Starting development server at http://..."
```

### Check for Template Errors
```bash
# Run server and check for errors
python manage.py runserver
```

## Browser-Specific Instructions

### Google Chrome
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Firefox
1. Press `Ctrl + Shift + Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Refresh page (F5)

### Edge
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear now"
4. Refresh page (F5)

## Production Server

If this is on production (scan2talk.in):

### Clear Server Cache
```bash
# SSH into server
ssh user@scan2talk.in

# Restart gunicorn/uwsgi
sudo systemctl restart gunicorn
# OR
sudo systemctl restart uwsgi

# Clear any server-side cache
python manage.py clear_cache  # if you have this command
```

### Clear CDN Cache (if using)
If you're using a CDN like Cloudflare:
1. Login to Cloudflare dashboard
2. Go to "Caching" → "Configuration"
3. Click "Purge Everything"

## Troubleshooting

### Issue: Still showing old version after hard refresh
**Solution**: Try incognito mode or different browser

### Issue: Changes not visible in incognito mode
**Solution**: Server needs restart or file wasn't saved properly

### Issue: Server shows template error
**Solution**: Check `templates/core/gateway_access.html` for syntax errors

## Files Modified

- `templates/core/gateway_access.html` - Removed Send Message button

## Expected Behavior

After clearing cache:
- ✅ Only "Call Owner" button visible
- ✅ Button is centered
- ✅ No "Send Message" option
- ✅ Clicking "Call Owner" initiates call

---

**Quick Fix**: Press `Ctrl + F5` to hard refresh!  
**Status**: Code updated, cache needs clearing  
**Date**: January 25, 2026
