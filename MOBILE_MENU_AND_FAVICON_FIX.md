# Mobile Menu & Favicon Fix

## Issues Fixed

### 1. Mobile Menu Home Button
**Problem:** Home button looked different from other buttons (plain text vs styled buttons)

**Solution:** Made Home button match the other buttons with border and styling
```html
<!-- Before: Plain text -->
<a href="..." class="block py-3 text-[#094067] font-medium">🏠 Home</a>

<!-- After: Styled button like others -->
<a href="..." class="block w-full py-3 px-4 text-center bg-white border-2 border-gray-400 text-gray-700 font-bold rounded-lg mb-3">
  🏠 Home
</a>
```

Now all 4 buttons (Home, Login, Distributor Login, Order QR) have consistent styling.

### 2. Favicon Not Showing
**Problem:** Favicon not displaying in browser tab

**Solution:** Updated favicon links with v4 and added PNG fallback
```html
<!-- SVG for modern browsers -->
<link rel="icon" type="image/svg+xml" href="/static/favicon.svg?v=4">

<!-- PNG fallback for compatibility -->
<link rel="icon" type="image/png" href="/static/tag/logo-sky.png?v=4">

<!-- Traditional favicon.ico -->
<link rel="shortcut icon" href="/favicon.ico?v=4">
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

**IMPORTANT:** You must clear browser cache to see the favicon:

### Method 1: Hard Refresh
- Press **Ctrl+Shift+R** (Windows/Linux)
- Press **Cmd+Shift+R** (Mac)

### Method 2: Clear Cache
- Press **Ctrl+Shift+Delete**
- Select "Cached images and files"
- Click "Clear data"

### Method 3: Incognito/Private Window
- Open new incognito/private window
- Visit https://scan2talk.in
- Favicon should show immediately

## Verify After Deployment

### 1. Check Mobile Menu:
- Open site on mobile or resize browser to mobile width
- Click hamburger menu (☰)
- Home button should now have gray border like other buttons

### 2. Check Favicon:
- Clear browser cache (Ctrl+Shift+Delete)
- Visit https://scan2talk.in
- Browser tab should show S2T icon
- If not, try incognito window

### 3. Test Favicon URLs:
```bash
# Check SVG exists
curl -I https://scan2talk.in/static/favicon.svg

# Check PNG fallback exists
curl -I https://scan2talk.in/static/tag/logo-sky.png

# Check favicon.ico redirect
curl -I https://scan2talk.in/favicon.ico
```

## Why Favicon Might Not Show

1. **Browser cache** - Most common issue, clear it!
2. **Static files not collected** - Run collectstatic
3. **Nginx not serving static** - Check nginx config
4. **Old version cached** - That's why we use ?v=4

## Files Modified
- `templates/base.html` - Fixed mobile menu Home button and favicon links

## Expected Results
✅ Mobile menu Home button matches other buttons
✅ Favicon shows in browser tab (after cache clear)
✅ Consistent styling across mobile navigation
