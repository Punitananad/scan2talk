# Meta Pixel Installation Complete ✅

## What Was Installed

### 1. Base Meta Pixel Code
**Location:** `templates/base.html` (in `<head>` section)

The Meta Pixel base code is now installed on **every page** of your website:
- Pixel ID: `1224905755716325`
- Tracks PageView on all pages automatically
- Installed in the header section as recommended by Facebook

### 2. Conversion Tracking Events

#### Order Page (`templates/core/order_tag.html`)
Added two key conversion events:

**a) InitiateCheckout Event**
- Fires when user lands on the order page
- Tracks that user is interested in purchasing
- Helps Facebook optimize for people likely to start checkout

**b) AddToCart Event**
- Fires when user clicks "Proceed to Payment" button
- Tracks: Product name, value (₹99), currency (INR)
- Helps Facebook optimize for people likely to add to cart

## Events Being Tracked

| Event | Page | When It Fires | Purpose |
|-------|------|---------------|---------|
| **PageView** | All pages | Page loads | Track all visitors |
| **InitiateCheckout** | Order page | Page loads | Track checkout intent |
| **AddToCart** | Order page | Click "Proceed to Payment" | Track add to cart |

## For Your Facebook Ads Manager

### Standard Events Installed:
1. ✅ **PageView** - Tracks all page visits
2. ✅ **InitiateCheckout** - Tracks when users view order page
3. ✅ **AddToCart** - Tracks when users click proceed to payment

### Recommended Next Steps in Facebook:

1. **Verify Pixel Installation**
   - Go to Events Manager
   - Check if events are firing
   - Use Facebook Pixel Helper Chrome extension

2. **Create Custom Audiences**
   - People who viewed order page (InitiateCheckout)
   - People who clicked proceed (AddToCart)
   - People who visited homepage

3. **Create Conversion Campaigns**
   - Optimize for InitiateCheckout
   - Optimize for AddToCart
   - Create lookalike audiences

4. **Set Up Retargeting**
   - Retarget people who viewed order page but didn't proceed
   - Retarget homepage visitors

## Testing the Pixel

### Method 1: Facebook Pixel Helper (Recommended)
1. Install [Facebook Pixel Helper](https://chrome.google.com/webstore/detail/facebook-pixel-helper/fdgfkebogiimcoedlicjlajpkdmockpc) Chrome extension
2. Visit your website: https://scan2talk.in
3. Click the extension icon
4. Should show: "Pixel ID 1224905755716325 found"

### Method 2: Facebook Events Manager
1. Go to Facebook Events Manager
2. Select your pixel (1224905755716325)
3. Click "Test Events"
4. Visit your website
5. Should see events appearing in real-time

### Method 3: Browser Console
1. Open your website
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Type: `fbq`
5. Should show the Facebook Pixel function

## Deployment

```bash
cd /var/www/scan2talk
git pull origin main
python3 manage.py collectstatic --noinput
systemctl restart gunicorn
systemctl restart nginx
```

## Verify After Deployment

1. **Visit homepage:**
   ```
   https://scan2talk.in
   ```
   - Should fire: PageView event

2. **Visit order page:**
   ```
   https://scan2talk.in/order-tag/
   ```
   - Should fire: PageView + InitiateCheckout events

3. **Click "Proceed to Payment":**
   - Should fire: AddToCart event with value ₹99

## Files Modified

1. `templates/base.html` - Added Meta Pixel base code
2. `templates/core/order_tag.html` - Added conversion tracking events

## Important Notes

- ✅ Pixel fires on ALL pages (installed in base template)
- ✅ Special tracking on order page (your main conversion page)
- ✅ Tracks button clicks for "Proceed to Payment"
- ✅ Includes value and currency for better optimization
- ✅ No impact on page load speed (async loading)

## Facebook Ads Optimization

With this pixel installed, you can now:

1. **Track ROI** - See which ads lead to orders
2. **Optimize Campaigns** - Facebook will show ads to people likely to convert
3. **Retarget Visitors** - Show ads to people who visited but didn't order
4. **Create Lookalikes** - Find people similar to your customers
5. **Measure Performance** - See exact conversion rates

## Privacy Compliance

The Meta Pixel is GDPR compliant when used with Facebook's tools. Consider adding:
- Cookie consent banner (if targeting EU)
- Privacy policy update mentioning Facebook Pixel
- Terms of service update

## Support

If events aren't showing in Facebook Events Manager:
1. Clear browser cache
2. Wait 20 minutes (events can take time to appear)
3. Check Facebook Pixel Helper extension
4. Verify pixel ID: 1224905755716325

## Success! 🎉

Your Meta Pixel is now installed and tracking conversions. You can start running Facebook ads with proper conversion tracking!
