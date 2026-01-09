# QR Batch PDF Download Feature

## What's New?

You can now **generate QR codes and download them as PDF in one click**!

---

## How to Use

### Option 1: Generate & Download PDF (Recommended)
1. Go to **Generate QR Codes** page
2. Fill in the form:
   - Batch Name (e.g., "Premium Parking - 2026-01-09")
   - Quantity (1-1000)
   - Category (required)
   - Purpose (optional)
   - Notes (optional)
3. Click the **BIG BLUE BUTTON**: "Generate & Download as PDF"
4. QR codes are generated AND PDF downloads automatically
5. PDF filename: `QR_Batch_{batch-name}.pdf`

### Option 2: Generate Only
1. Fill in the same form
2. Click **"Generate Only"** (green button)
3. QR codes are created
4. Go to QR Dashboard to download later

### Option 3: Download Existing Batch
1. Go to **QR Dashboard**
2. Filter by batch name
3. Click **"Download as PDF"** or **"Download as ZIP"**

---

## Button Layout

```
┌─────────────────────────────────────────────┐
│                                             │
│  [Generate & Download as PDF]  ← BIG BLUE  │
│                                             │
├─────────────────────┬───────────────────────┤
│  [Generate Only]    │  [View Dashboard]     │
│  (Green)            │  (Gray)               │
└─────────────────────┴───────────────────────┘
```

---

## PDF Details

### Filename Format
- `QR_Batch_{batch-name}.pdf`
- Example: `QR_Batch_Premium-Parking-2026-01-09-A7B3.pdf`

### PDF Layout
- **4 QR codes per row**
- **6 rows per page**
- **24 QR codes per page**
- Each QR code shows:
  - QR image (scannable)
  - QR code text (e.g., "ABC12345")
  - "Scan to activate" instruction

### PDF Header
- Batch name
- Total number of QR codes
- Professional layout

---

## Use Cases

### Scenario 1: Quick Distribution
1. Generate 50 QR codes for parking lot
2. Download PDF immediately
3. Print and distribute
4. Users scan to activate

### Scenario 2: Bulk Generation
1. Generate 500 QR codes
2. Choose "Generate Only"
3. Download PDF later from dashboard
4. Or download as ZIP for individual images

### Scenario 3: Re-download
1. Already generated batch
2. Go to QR Dashboard
3. Filter by batch name
4. Download PDF again (no regeneration needed)

---

## Benefits

✅ **One-Click Workflow** - Generate and download in single action
✅ **Automatic Naming** - PDF uses batch name (no manual renaming)
✅ **Print-Ready** - Professional layout, ready to print
✅ **Flexible** - Can still generate without downloading
✅ **Re-downloadable** - Download same batch multiple times

---

## Technical Details

### Backend
- Action parameter: `generate_and_download_pdf` or `generate_only`
- Redirects to PDF download after generation
- Uses batch name in filename

### Frontend
- Two submit buttons with different actions
- Primary button (blue) = Generate & Download
- Secondary button (green) = Generate Only

### PDF Generation
- Uses ReportLab library
- A4 page size
- 4x6 grid (24 codes per page)
- Includes QR image + text + instructions

---

## Tips

1. **Use descriptive batch names** - They become the PDF filename
2. **Generate & Download** is fastest for immediate use
3. **Generate Only** if you need to review first
4. **Download from Dashboard** to get PDF again without regenerating

---

## Example Workflow

```
Admin wants 100 QR codes for premium parking:

1. Click "Generate QR Codes"
2. Enter:
   - Batch Name: "Premium-Parking-Lot-A"
   - Quantity: 100
   - Category: "Premium Prepaid"
   - Purpose: "VIP parking section"
3. Click "Generate & Download as PDF"
4. Wait 5-10 seconds
5. PDF downloads: "QR_Batch_Premium-Parking-Lot-A-X7Y2.pdf"
6. Print PDF
7. Distribute QR stickers
8. Done! ✅
```

---

**Result:** Generate and download QR codes in one smooth workflow!
