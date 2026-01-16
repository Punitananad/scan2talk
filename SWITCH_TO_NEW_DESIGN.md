# Switch to New Trippi Design - Step by Step

## Current Status ✅

- ✅ Trippi assets copied to `static/trippi/`
- ✅ New landing page created: `templates/core/home_new.html`
- ✅ Base template updated with new navbar/footer
- ✅ Development server running at http://127.0.0.1:8000/

## Quick Switch (2 Minutes)

### Method 1: Replace Home View Template

**File:** `apps/core/views.py`

Find the home view function and change the template:

```python
# BEFORE
def home(request):
    return render(request, 'core/home.html')

# AFTER
def home(request):
    return render(request, 'core/home_new.html')
```

**That's it!** Refresh your browser to see the new design.

---

### Method 2: Add New URL (Keep Both)

If you want to keep both designs accessible:

**File:** `apps/core/urls.py`

```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),              # Old design
    path('new/', views.home_new, name='home_new'),  # New design
    # ... other URLs
]
```

**File:** `apps/core/views.py`

```python
def home(request):
    return render(request, 'core/home.html')  # Old design

def home_new(request):
    return render(request, 'core/home_new.html')  # New design
```

**Access:**
- Old design: `http://127.0.0.1:8000/`
- New design: `http://127.0.0.1:8000/new/`

---

## Verify the Switch

1. **Open your browser:** http://127.0.0.1:8000/
2. **You should see:**
   - Modern blue color scheme (#3DA9FC)
   - "Connect Without Sharing Your Number" headline
   - Animated elements on scroll
   - Testimonial carousel
   - FAQ accordion

3. **If you see the old design:**
   - Clear browser cache (Ctrl + Shift + R)
   - Check that you saved the views.py file
   - Restart Django server if needed

---

## Rollback (If Needed)

To go back to the old design:

```python
# In apps/core/views.py
def home(request):
    return render(request, 'core/home.html')  # Back to original
```

---

## Customization After Switch

### 1. Update Hero Text
**File:** `templates/core/home_new.html` (Line ~30)

```html
<h1 class="text-5xl sm:text-6xl md:text-7xl mb-4 font-extrabold text-[#094067] leading-tight">
    Connect Without <span class="text-[#3DA9FC]">Sharing</span> Your Number
</h1>
```

### 2. Update Testimonials
**File:** `templates/core/home_new.html` (Line ~150)

```html
<div class="swiper-slide ...">
    <p>"Your testimonial text here"</p>
    <div class="flex items-center space-x-4">
        <div class="w-10 xl:w-12 h-10 xl:h-12 rounded-full bg-[#3DA9FC] text-white flex items-center justify-center font-bold">
            RS
        </div>
        <div>
            <h6 class="text-[#094067] font-medium">Customer Name</h6>
            <p class="text-sm text-[#5F6C7B]">Job Title</p>
        </div>
    </div>
</div>
```

### 3. Update FAQ
**File:** `templates/core/home_new.html` (Line ~180)

```html
<div class="w-full px-7 py-5 border-b ...">
    <span class="w-full font-medium text-base sm:text-lg">Your question here?</span>
    ...
</div>
```

### 4. Update CTA Buttons
**File:** `templates/core/home_new.html` (Line ~40, ~90, ~140, ~200)

```html
<a href="{% url 'core:order_tag' %}" class="...">
    Order Your QR Code
</a>
```

---

## Testing Checklist

After switching, test these:

- [ ] Hero section displays correctly
- [ ] Images load properly
- [ ] Buttons link to correct pages
- [ ] Testimonial carousel works
- [ ] FAQ accordion expands/collapses
- [ ] Mobile responsive (resize browser)
- [ ] Navbar dropdown works (if logged in)
- [ ] Footer links work
- [ ] Scroll animations trigger
- [ ] All CTAs point to correct URLs

---

## Performance Check

### Load Time
- Target: < 3 seconds
- Check: Open DevTools → Network tab

### Image Optimization
```bash
# If images are slow, compress them
# Use tools like TinyPNG or ImageOptim
```

### CDN Resources
All external resources load from CDN:
- ✅ Tailwind CSS
- ✅ Swiper.js
- ✅ AOS
- ✅ Alpine.js
- ✅ Google Fonts

---

## Production Deployment

Before deploying to production:

1. **Collect Static Files**
```bash
python manage.py collectstatic
```

2. **Test on Staging**
- Deploy to staging environment first
- Test all functionality
- Check mobile responsiveness

3. **Update Environment**
```bash
# If using environment variables
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

4. **Deploy**
```bash
# Use your deployment script
./deploy.sh
# or
./ramban_deploy_s2t.sh
```

---

## Support

If you encounter issues:

1. **Check Django logs**
```bash
# In terminal where server is running
# Look for error messages
```

2. **Check browser console**
```
F12 → Console tab
Look for JavaScript errors
```

3. **Verify file paths**
```python
# In Django shell
python manage.py shell
>>> from django.template.loader import get_template
>>> get_template('core/home_new.html')
```

---

## Summary

**To switch to new design:**
1. Edit `apps/core/views.py`
2. Change `'core/home.html'` to `'core/home_new.html'`
3. Save and refresh browser

**That's it! 🎉**

The new Trippi-inspired design is now live on your Scan2Talk platform.
