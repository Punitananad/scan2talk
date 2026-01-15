# How to Preview QR Tags Before Download

## Step-by-Step Guide

### Step 1: Generate QR Codes
1. Go to: `http://localhost:8000/gateways/gqr/`
2. Fill in the form:
   - Batch Name: e.g., "Test Batch - 2026-01-15"
   - Quantity: e.g., 10
   - Category: Select a category
3. Click **"Generate & Download as PDF"** OR **"Generate Only"**

### Step 2: Go to QR Dashboard
1. After generation, click **"View Dashboard"** button
2. OR navigate to: `http://localhost:8000/gateways/qr/dashboard/`

### Step 3: Select Your Batch
1. Find the **"Filters & Batch Downloads"** section
2. In the **"Batch"** dropdown, select your batch
   - Example: "Test Batch - 2026-01-15-ABC1 (10 codes)"
3. Click **"Apply Filters"** button

### Step 4: Preview Sample
1. After selecting batch, you'll see buttons appear:
   ```
   [👁️ Preview Sample] [📄 Download PDF] [📦 Download ZIP] [🗑️ Delete Batch]
   ```
2. Click **"👁️ Preview Sample"** (purple button)
3. A popup window opens showing the first QR tag

### Step 5: Verify and Download
1. Check the preview:
   - Is QR in the yellow box? ✓
   - Is it centered? ✓
   - Does it look good? ✓
2. If preview looks good, close popup
3. Click **"📄 Download PDF"** to get full batch

## Visual Flow

```
Generate QR Codes
       ↓
View Dashboard
       ↓
Select Batch from Dropdown
       ↓
Click "Apply Filters"
       ↓
[👁️ Preview Sample] Button Appears
       ↓
Click to See Preview
       ↓
Verify QR Placement
       ↓
Download PDF if Good
```

## Button Locations

### On Generation Page (`/gateways/gqr/`):
- **Generate & Download as PDF** - Generates and downloads immediately
- **Generate Only** - Just creates QR codes
- **View Dashboard** - Go to dashboard to preview

### On Dashboard Page (`/gateways/qr/dashboard/`):
After selecting a batch:
- **👁️ Preview Sample** (Purple) - Preview first QR tag
- **📄 Download PDF** (Red) - Download full PDF
- **📦 Download ZIP** (Green) - Download as ZIP
- **🗑️ Delete Batch** (Gray) - Delete entire batch

## Preview Features

The preview shows:
- ✅ Full template image (`static/tag/pqr-tg.jpeg`)
- ✅ QR code at position (1405, 165)
- ✅ QR size: 360x360 pixels
- ✅ High quality: 300 DPI
- ✅ First QR from the batch

## Troubleshooting

### "I don't see the Preview button"
**Solution**: You need to select a batch first
1. Go to QR Dashboard
2. Use the "Batch" dropdown
3. Select your batch
4. Click "Apply Filters"
5. Preview button will appear

### "Preview opens but shows error"
**Solution**: Check template file exists
```bash
ls static/tag/pqr-tg.jpeg
```

### "Preview shows QR in wrong position"
**Solution**: The code uses fixed coordinates (1405, 165)
- This should place QR in the yellow box
- If not, check your template dimensions

## Quick Access URLs

- **Generate QR**: `http://localhost:8000/gateways/gqr/`
- **QR Dashboard**: `http://localhost:8000/gateways/qr/dashboard/`
- **Preview** (after selecting batch): Appears automatically

## Tips

1. **Always preview first** before printing
2. **Check QR position** in yellow box
3. **Verify quality** at 300 DPI
4. **Test scan** the preview QR with your phone
5. **Download PDF** only after preview looks good

---

**Need Help?**
- Preview not showing? Select a batch from dropdown first
- QR in wrong position? Check template file
- Can't download? Try preview first to verify

**Status**: ✅ Preview feature is ready to use
