# HTML-Based QR Tag Generation System

## Overview
The QR tag generation system now uses **HTML templates** instead of image overlays. This provides:
- ✅ Cleaner, more maintainable code
- ✅ Easy design updates (just edit HTML/CSS)
- ✅ Consistent preview and PDF output
- ✅ Better print quality
- ✅ No dependency on template images for QR placement
- ✅ **Windows compatible** (uses xhtml2pdf instead of weasyprint)

## Key Files

### Templates
1. **`templates/gateways/tag_print_design.html`**
   - Single tag design with HTML/CSS
   - Used for preview and single tag display
   - Accepts `qr_code_data` (base64 encoded QR image)

2. **`templates/gateways/tag_batch_print.html`**
   - Batch printing layout (2x4 grid = 8 tags per A4 page)
   - Accepts `qr_pages` (list of pages, each with up to 8 QR codes)
   - Optimized for A4 printing

### Backend
- **`apps/gateways/qr_download_views.py`**
  - `preview_batch_sample()` - Shows single tag preview
  - `download_batch_pdf()` - Generates PDF using HTML template
  - `generate_qr_base64()` - Converts QR code to base64 for embedding

## How It Works

### 1. QR Code Generation
```python
# Generate QR code as base64 string
qr_code_data = generate_qr_base64(qr.qr_code)
```

### 2. HTML Template Rendering
```django
<!-- In template -->
<img src="data:image/png;base64,{{ qr_code_data }}" alt="QR Code">
```

### 3. PDF Conversion
```python
# Using xhtml2pdf (Windows compatible)
from xhtml2pdf import pisa
html_string = render_to_string('gateways/tag_batch_print.html', context)
result = io.BytesIO()
pdf = pisa.pisaDocument(io.BytesIO(html_string.encode("UTF-8")), result)
```

## Installation

### Install xhtml2pdf
```bash
pip install xhtml2pdf
```

**Note:** xhtml2pdf is pure Python and works on all platforms without system dependencies!

## Usage

### Admin Workflow
1. Go to `/gqr/` (Generate QR page)
2. Enter batch details and quantity
3. Click "Generate & Download PDF"
4. Preview page shows sample tag
5. Click "Download PDF" to get printable A4 sheets

### API Endpoints
- `GET /gateways/batch/<batch_number>/preview/` - Preview single tag
- `GET /gateways/batch/<batch_number>/download-pdf/` - Download PDF
- `GET /gateways/batch/<batch_number>/download-zip/` - Download QR images as ZIP

## Design Customization

### Modify Tag Design
Edit `templates/gateways/tag_print_design.html`:

```html
<!-- Change colors -->
<style>
.highlight {
  background: #f5c400; /* Yellow highlight */
}

.qr-box {
  background: repeating-linear-gradient(
    45deg,
    #000 0 1.5mm,
    #f5c400 1.5mm 3mm  /* Striped border */
  );
}
</style>
```

### Adjust Layout
```css
/* Tag dimensions */
.tag {
  width: 100mm;
  height: 70mm;
}

/* QR box size */
.qr-box {
  width: 38mm;
  height: 38mm;
}
```

### Change Grid Layout
Edit `templates/gateways/tag_batch_print.html`:
```css
.grid {
  grid-template-columns: repeat(2, 1fr); /* 2 columns */
  grid-template-rows: repeat(4, 1fr);    /* 4 rows */
}
```

## Advantages Over Image-Based System

### Old System (Image Overlay)
- ❌ Required template image file
- ❌ Complex PIL image manipulation
- ❌ Hard to adjust QR position
- ❌ Preview and PDF could look different
- ❌ Difficult to update design

### New System (HTML Template)
- ✅ Pure HTML/CSS design
- ✅ Easy to customize
- ✅ Consistent preview and PDF
- ✅ No image dependencies for layout
- ✅ Better maintainability
- ✅ **Windows compatible**

## Troubleshooting

### PDF Generation Fails
**Error:** `xhtml2pdf is not installed`
**Solution:** Run `pip install xhtml2pdf`

### QR Code Not Showing
**Issue:** Base64 encoding failed
**Check:** Ensure `generate_qr_code()` in `apps/core/utils.py` returns valid image

### Layout Issues in PDF
**Issue:** Tags overlapping or misaligned
**Solution:** Adjust CSS in `tag_batch_print.html`:
```css
.grid {
  gap: 5mm; /* Increase spacing */
}
```

### Print Quality Issues
**Issue:** Blurry QR codes
**Solution:** Increase QR code size in template:
```css
.qr-box {
  width: 40mm;  /* Larger QR */
  height: 40mm;
}
```

## Testing

### Test Single Tag Preview
```bash
# Visit in browser
http://localhost:8000/gateways/batch/BATCH-NAME/preview/
```

### Test PDF Generation
```bash
# Download PDF
http://localhost:8000/gateways/batch/BATCH-NAME/download-pdf/
```

### Test in Production
```bash
# Ensure xhtml2pdf is installed on server
pip install xhtml2pdf

# No system dependencies needed!
```

## Why xhtml2pdf Instead of weasyprint?

**weasyprint** requires system libraries (libgobject, pango, etc.) which are:
- ❌ Difficult to install on Windows
- ❌ Require admin privileges
- ❌ Can cause deployment issues

**xhtml2pdf** is:
- ✅ Pure Python (no system dependencies)
- ✅ Works on Windows, Linux, macOS
- ✅ Easy to install and deploy
- ✅ Sufficient for our needs

## Migration Notes

### From Old System
The old image-based system is completely replaced. No migration needed for existing QR codes - they will work with the new system automatically.

### Deployment
1. Update `requirements.txt` (already done)
2. Install dependencies: `pip install -r requirements.txt`
3. Restart server
4. Test PDF generation

## Summary

The system now uses **HTML templates** with **xhtml2pdf** for QR tag generation, making it easier to maintain, customize, and deploy on any platform including Windows.

**Key Benefits:**
- Clean, maintainable code
- Easy design updates
- Consistent output
- Better print quality
- No image dependencies
- **Windows compatible**
