# Preview Feature Added ✅

## What's New

Added a **Preview Sample** button that shows you exactly how the QR code will look on the template BEFORE downloading the full PDF.

## How It Works

### 1. Preview Button Location
- Go to QR Dashboard: `/qr/dashboard/`
- Select a batch from the dropdown filter
- You'll see a new **👁️ Preview Sample** button (purple)

### 2. What Preview Shows
- Opens in a new popup window (800x600)
- Shows the FIRST QR code from the batch
- QR is placed at EXACT position: (1405, 165)
- QR size: 360x360 pixels
- Template: `static/tag/pqr-tg.jpeg`
- High quality: 300 DPI

### 3. Button Order
```
[👁️ Preview Sample] [📄 Download PDF] [📦 Download ZIP] [🗑️ Delete Batch]
```

## Files Modified

### 1. apps/gateways/qr_download_views.py
Added new view:
```python
@staff_member_required
def preview_batch_sample(request, batch_number):
    """Preview a single sample tag before downloading PDF"""
```

### 2. apps/gateways/urls.py
Added new route:
```python
path('qr/batch/<str:batch_number>/preview/', 
     qr_download_views.preview_batch_sample, 
     name='preview_batch_sample'),
```

### 3. templates/gateways/qr_dashboard.html
Added preview button:
```html
<button 
   onclick="window.open('{% url 'gateways:preview_batch_sample' batch_filter %}', '_blank', 'width=800,height=600')"
   class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 text-sm">
    👁️ Preview Sample
</button>
```

## Usage Flow

1. **Generate Batch**
   - Go to `/gqr/`
   - Generate QR codes (e.g., 10 codes)

2. **Preview**
   - Go to `/qr/dashboard/`
   - Select your batch from dropdown
   - Click **👁️ Preview Sample**
   - New window opens showing the first tag

3. **Verify**
   - Check QR position in yellow box
   - Verify it's centered correctly
   - Check print quality

4. **Download**
   - If preview looks good, click **📄 Download PDF**
   - Get full PDF with all tags (8 per page)

## Preview Features

- ✅ Shows actual template with QR overlay
- ✅ Uses FIXED coordinates (1405, 165)
- ✅ QR size: 360x360 pixels
- ✅ High quality: 300 DPI
- ✅ Opens in popup window
- ✅ No download required
- ✅ Instant preview
- ✅ Shows first QR from batch

## Technical Details

### Preview View
```python
def preview_batch_sample(request, batch_number):
    # Get first QR from batch
    qr = PreGeneratedQR.objects.filter(batch_number=batch_number).first()
    
    # Load template
    template = Image.open('static/tag/pqr-tg.jpeg')
    
    # Generate QR
    qr_img = generate_qr_code(activation_url)
    
    # Paste at FIXED position
    qr_img = qr_img.resize((360, 360))
    template.paste(qr_img, (1405, 165))
    
    # Return as PNG
    return HttpResponse(image, content_type='image/png')
```

### URL Pattern
```
/qr/batch/<batch_number>/preview/
```

### Button Action
```javascript
window.open(preview_url, '_blank', 'width=800,height=600')
```

## Benefits

1. **No Wasted Prints**: Verify before printing
2. **Quick Check**: Instant preview, no download
3. **Position Verification**: See exact QR placement
4. **Quality Check**: Verify 300 DPI quality
5. **Easy Access**: One click from dashboard

## Deployment

```bash
# Pull latest code
git pull origin main

# Restart server
sudo systemctl restart gunicorn

# Test
1. Go to /qr/dashboard/
2. Select a batch
3. Click "Preview Sample"
4. Verify QR is in yellow box
5. Download PDF if preview looks good
```

## Screenshots Flow

```
Dashboard → Select Batch → Preview Sample → [Popup Opens] → Verify → Download PDF
```

## Error Handling

- If batch has no QR codes: Returns 404
- If template not found: Returns 404
- If generation fails: Returns 500 with error message

## Future Enhancements

Possible additions:
- Preview all QR codes (not just first)
- Preview with pagination
- Download single preview as PNG
- Adjust position in preview before PDF

---

**Status**: ✅ Ready to use  
**Last Updated**: January 15, 2026  
**Feature**: Preview before download
