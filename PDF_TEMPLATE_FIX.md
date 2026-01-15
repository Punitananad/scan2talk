# PDF Template Overlay Fix ✅

## Problem
PDF was showing only QR codes without the template image overlay.

## Root Causes Fixed

1. **Wrong filename**: Code was looking for `pre-tg.jpeg` but actual file is `pqr-tg.jpeg`
2. **Low DPI**: Template was being resized at 72 DPI (too low quality)
3. **No error logging**: Errors were silent, making debugging impossible
4. **No fallback**: If template failed, PDF generation would break

## Solution Applied

### 1. Fixed Template Path
```python
# Before (WRONG):
template_path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'pre-tg.jpeg')

# After (CORRECT):
template_path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'pqr-tg.jpeg')
```

### 2. Improved Quality
- Increased DPI from 72 to 288 (4x better quality)
- Better image resizing with LANCZOS filter
- Higher resolution template processing

### 3. Added Comprehensive Logging
- Logs every step of the process
- Shows template size, QR position, detected areas
- Helps debug issues quickly

### 4. Added Robust Error Handling
- Checks if template exists before processing
- Falls back to simple QR if template fails
- Continues processing even if one QR fails

## Files Modified

1. **apps/gateways/qr_download_views.py**
   - Fixed template path: `pqr-tg.jpeg`
   - Increased DPI to 288
   - Added comprehensive logging
   - Improved error handling
   - Better fallback mechanism

## Testing

### Test 1: Verify Template Exists
```bash
ls -la static/tag/pqr-tg.jpeg
```

Should show the file exists.

### Test 2: Run Test Script
```bash
python test_template_overlay.py
```

This will:
- Check if template exists
- Load and process template
- Generate test QR code
- Overlay QR on template
- Save output as `test_tag_output.png`

**Check the output file** to verify QR is correctly positioned!

### Test 3: Generate Actual PDF
1. Go to: `/gqr/`
2. Generate a batch (e.g., 5 QR codes)
3. Select "Generate & Download PDF"
4. Open the PDF

**Expected Result**: Each page should show 8 tags (2x4 grid) with QR codes overlaid on your template image.

## Deployment

### Quick Deploy:
```bash
# On server
cd /path/to/project
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # Ensures numpy is installed
sudo systemctl restart gunicorn

# Test it
python test_template_overlay.py
```

### Check Logs:
```bash
# View Django logs
sudo journalctl -u gunicorn -f

# Look for these messages:
# ✅ "Using template: /path/to/static/tag/pqr-tg.jpeg"
# ✅ "Template loaded: (width, height)"
# ✅ "Detected QR area: center=(x, y), size=..."
# ✅ "Successfully created tag 1"
```

## What You'll See

### Before (Wrong):
- PDF with just QR codes on white background
- No template image
- Just QR code + text label

### After (Correct):
- PDF with full template image
- QR code overlaid on the "Place Your QR Here" area
- Professional print-ready tags
- 8 tags per A4 page (2 columns × 4 rows)

## Template Requirements

Your template (`static/tag/pqr-tg.jpeg`) should have:
- A bright/white area where you want the QR code
- Text like "Place Your QR Here" in that area
- The code automatically detects the brightest area and centers QR there

If detection fails, it falls back to center of template at 35% width.

## Troubleshooting

### Issue: Still showing plain QR codes
**Solution**: 
1. Check template path: `ls static/tag/pqr-tg.jpeg`
2. Check logs for errors: `sudo journalctl -u gunicorn -f`
3. Run test script: `python test_template_overlay.py`

### Issue: QR code in wrong position
**Solution**:
1. Check your template has a bright/white area
2. Adjust detection threshold in code (line with `np.percentile(gray, 90)`)
3. Or manually set position by modifying fallback values

### Issue: Low quality images
**Solution**:
- Already fixed! DPI increased to 288
- If still low, increase `target_width` in code (currently `tag_width * 4`)

### Issue: Template not loading
**Solution**:
```bash
# Check file exists
ls -la static/tag/pqr-tg.jpeg

# Check permissions
chmod 644 static/tag/pqr-tg.jpeg

# Check Django can access it
python manage.py shell
>>> from django.conf import settings
>>> import os
>>> path = os.path.join(settings.BASE_DIR, 'static', 'tag', 'pqr-tg.jpeg')
>>> os.path.exists(path)
True  # Should be True
```

## Debug Commands

```bash
# Test template overlay
python test_template_overlay.py

# Check output
ls -la test_tag_output.png

# View with image viewer
xdg-open test_tag_output.png  # Linux
open test_tag_output.png      # Mac
start test_tag_output.png     # Windows

# Check Django logs
sudo journalctl -u gunicorn -f | grep -i "template\|qr"

# Restart server
sudo systemctl restart gunicorn
```

## Success Checklist

- [ ] Template file exists at `static/tag/pqr-tg.jpeg`
- [ ] numpy installed (`pip list | grep numpy`)
- [ ] Test script runs successfully
- [ ] `test_tag_output.png` shows QR on template
- [ ] PDF generation works from admin panel
- [ ] PDF shows template images (not just QR codes)
- [ ] QR codes are positioned correctly on template
- [ ] 8 tags per page in 2×4 grid
- [ ] Print quality is good (288 DPI)

---

**Status**: Ready to deploy
**Last Updated**: January 15, 2026
