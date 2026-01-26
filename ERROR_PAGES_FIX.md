# Custom Error Pages for Production

## Problem
When `DEBUG = False` in production, Django was showing detailed error pages that exposed:
- All URL patterns
- Internal application structure
- Security-sensitive information

## Solution
Implemented custom error handlers and beautiful error pages that:
- Hide sensitive information
- Provide user-friendly error messages
- Maintain brand consistency
- Guide users back to working pages

## Files Created

### 1. Error Handler Views
**File:** `apps/core/error_handlers.py`
- `handler404` - Page not found
- `handler500` - Internal server error
- `handler403` - Access denied
- `handler400` - Bad request

### 2. Error Templates
**Directory:** `templates/errors/`
- `404.html` - Beautiful 404 page with navigation
- `500.html` - Server error page (standalone, no base template)
- `403.html` - Access denied page
- `400.html` - Bad request page

### 3. URL Configuration
**File:** `gateway_platform/urls.py`
- Added custom error handler references
- Configured for production use

### 4. Gateway Detail Fix
**Files:**
- `templates/gateways/gateway_detail.html` - New template for gateway details
- `apps/gateways/views.py` - Updated to use correct template

## Features

### User-Friendly Design
- Clean, modern interface
- Consistent with brand colors
- Mobile responsive
- Clear call-to-action buttons

### Navigation Options
- Go to Homepage button
- Go Back button
- Contact support link

### Security
- No URL pattern exposure
- No stack traces
- No sensitive information

## Testing

### Local Testing (with DEBUG=False)
1. Set `DEBUG=False` in `.env`
2. Set `ALLOWED_HOSTS` properly
3. Run: `python manage.py runserver --insecure`
4. Visit: `http://localhost:8000/nonexistent-page`

### Production Testing
1. Visit: `https://scan2talk.in/nonexistent-page`
2. Should see custom 404 page
3. No URL patterns should be visible

## Deployment

### Quick Deploy (Windows)
```powershell
.\deploy_error_pages.ps1
```

### Quick Deploy (Linux/Mac)
```bash
bash deploy_error_pages.sh
```

### Manual Deployment
1. **Push changes to repository:**
   ```bash
   git add .
   git commit -m "Add custom error pages"
   git push origin main
   ```

2. **On production server:**
   ```bash
   cd /root/CPA
   git pull origin main
   python manage.py collectstatic --noinput
   systemctl restart gunicorn
   systemctl restart nginx
   ```

3. **Verify:**
   - Visit: https://scan2talk.in/test-404
   - Should see custom 404 page

## Error Page Customization

### Changing Colors
Edit the Tailwind classes in each template:
- `from-blue-50 to-purple-50` - Background gradient
- `text-blue-600` - Link colors
- `from-blue-600 to-purple-600` - Button gradient

### Changing Messages
Edit the text in each template:
- `<h2>` - Main error title
- `<p>` - Error description
- Button text and links

### Adding Branding
Add your logo to each template:
```html
<img src="{% static 'your-logo.png' %}" alt="Logo" class="h-12 mb-4">
```

## Important Notes

### 500 Error Template
The `500.html` template:
- Does NOT extend `base.html`
- Includes Tailwind CDN directly
- Uses hardcoded URLs (no `{% url %}` tags)
- This is because 500 errors may occur when Django can't process templates

### DEBUG Setting
- **Development:** `DEBUG=True` - Shows detailed errors
- **Production:** `DEBUG=False` - Shows custom error pages

### ALLOWED_HOSTS
When `DEBUG=False`, you MUST set `ALLOWED_HOSTS`:
```python
ALLOWED_HOSTS = ['scan2talk.in', 'www.scan2talk.in', '68.183.91.15']
```

## Troubleshooting

### Error pages not showing
1. Check `DEBUG=False` in production
2. Verify error handlers in `urls.py`
3. Check template files exist in `templates/errors/`
4. Restart gunicorn: `systemctl restart gunicorn`

### 500 error page not working
1. Check `500.html` doesn't use `{% url %}` tags
2. Verify it doesn't extend `base.html`
3. Use hardcoded URLs only

### Static files not loading
1. Run: `python manage.py collectstatic --noinput`
2. Check nginx configuration
3. Verify `STATIC_ROOT` setting

## Security Checklist

✅ Custom error pages created
✅ URL patterns hidden
✅ Stack traces disabled
✅ Sensitive info removed
✅ User-friendly messages
✅ Navigation provided
✅ Contact support available

## Additional Security Settings

Add to `settings.py` for production:
```python
# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## Support

If you encounter issues:
1. Check Django logs: `tail -f /var/log/gunicorn/error.log`
2. Check nginx logs: `tail -f /var/log/nginx/error.log`
3. Test locally with `DEBUG=False`
4. Verify all templates exist

## Summary

✅ **Problem Fixed:** URL patterns no longer exposed in production
✅ **User Experience:** Beautiful, helpful error pages
✅ **Security:** Sensitive information hidden
✅ **Branding:** Consistent with site design
✅ **Navigation:** Easy return to working pages

The application is now production-ready with proper error handling!
