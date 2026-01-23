# Duplicate QR Printing System

## ✅ IMPLEMENTATION COMPLETE

Each QR code is now printed **twice** (in duplicate) on the same page, with scissor cut marks for easy separation.

---

## 🎯 How It Works

### Before (Old System)
- Generate 10 QR codes → Get 10 unique tags
- 1 page = 8 different QR codes
- No duplicates

### After (New System)
- Generate 10 QR codes → Get 20 tags (10 originals + 10 copies)
- 1 page = 4 unique QR codes × 2 copies each = 8 tags total
- Each QR printed twice side-by-side

---

## 📐 Page Layout

### A4 Page Structure (2 columns × 4 rows = 8 tags)

```
┌─────────────────────────────────────────┐
│  QR1 (Original)  ✂  QR1 (Copy)         │
├─────────────────────────────────────────┤
│  QR2 (Original)  ✂  QR2 (Copy)         │
├─────────────────────────────────────────┤
│  QR3 (Original)  ✂  QR3 (Copy)         │
├─────────────────────────────────────────┤
│  QR4 (Original)  ✂  QR4 (Copy)         │
└─────────────────────────────────────────┘

✂ = Scissor cut marks (dashed lines)
```

---

## ✂️ Cut Marks

### Visual Indicators
- **Vertical dashed line** down the middle (separates left/right columns)
- **Horizontal dashed lines** between rows
- **Scissor icons (✂)** at cut points
- **Light gray color** - visible but not intrusive

### Where to Cut
1. **Vertical cut** - Down the middle to separate original from copy
2. **Horizontal cuts** - Between each row to separate different QRs

---

## 💡 Use Cases

### Scenario 1: Customer Purchase
```
Customer buys 1 QR tag
→ You give them: Original tag
→ You keep: Copy tag (for records/backup)
```

### Scenario 2: Distributor Sales
```
Distributor gets 10 QR codes
→ Receives: 10 original tags (left column)
→ You keep: 10 copy tags (right column) for tracking
```

### Scenario 3: Bulk Orders
```
Company orders 50 QR codes
→ They get: 50 original tags
→ You keep: 50 copy tags for inventory management
```

---

## 📊 Quantity Calculation

### Examples

| QRs Generated | Total Tags Printed | Pages Needed |
|---------------|-------------------|--------------|
| 4 QRs | 8 tags (4×2) | 1 page |
| 8 QRs | 16 tags (8×2) | 2 pages |
| 10 QRs | 20 tags (10×2) | 3 pages |
| 20 QRs | 40 tags (20×2) | 5 pages |
| 50 QRs | 100 tags (50×2) | 13 pages |

**Formula:** Pages needed = ceil(QR_count × 2 / 8)

---

## 🖨️ Printing Instructions

### Step 1: Generate Batch
```
Admin Panel → Generate QR Batch
Enter quantity: 10
→ System creates 10 unique QR codes
```

### Step 2: Preview
```
Click "Preview Batch"
→ See 20 tags (10 originals + 10 copies)
→ Arranged in pairs with cut marks
```

### Step 3: Print
```
Print from browser (Ctrl+P or Cmd+P)
→ Select "Print backgrounds" option
→ Print all pages
```

### Step 4: Cut
```
1. Cut down the middle (vertical line)
   → Separates originals (left) from copies (right)

2. Cut between rows (horizontal lines)
   → Separates different QR codes

Result: 10 original tags + 10 copy tags
```

---

## 📦 Organization Tips

### After Cutting

**Option 1: Separate Stacks**
```
Stack 1: All originals (for customers)
Stack 2: All copies (for your records)
```

**Option 2: Paired Storage**
```
Envelope 1: QR1 original + QR1 copy
Envelope 2: QR2 original + QR2 copy
etc.
```

**Option 3: Customer Ready**
```
Give customer: Original tag
File copy: In customer folder/record
```

---

## 🎨 Visual Features

### Cut Mark Design
- **Dashed lines** - Easy to see, professional look
- **Scissor icons (✂)** - Clear cutting indicators
- **Light gray color** - Visible but not distracting
- **Print-friendly** - Shows on both color and B&W printers

### Tag Features (Both Original & Copy)
- Same QR code
- Same category indicator (colored dot)
- Same design and layout
- Identical in every way

---

## 🔧 Technical Details

### View Changes
File: `apps/gateways/qr_download_views.py`

```python
# Duplicate each QR code
for qr in qr_codes:
    qr_data = {...}
    qr_data_list.append(qr_data)  # Original
    qr_data_list.append(qr_data)  # Copy
```

### Template Changes
File: `templates/gateways/tag_print_design.html`

```css
/* Cut marks */
.cut-line-horizontal { border-top: 1px dashed #94a3b8; }
.cut-line-vertical { border-left: 1px dashed #94a3b8; }
.scissor-icon { font-size: 3mm; color: #64748b; }
```

---

## 📋 Benefits

### For Business
✅ **Backup copies** - Always have a spare
✅ **Record keeping** - Keep copy for tracking
✅ **Quality control** - Verify before giving to customer
✅ **Inventory management** - Track what's been distributed

### For Customers
✅ **Professional** - Clean, organized tags
✅ **Easy to cut** - Clear cut marks
✅ **Quality** - Same as original

### For Distributors
✅ **Tracking** - Keep copies of distributed tags
✅ **Accountability** - Know which tags were given out
✅ **Records** - File copies for reference

---

## 🧪 Testing

### Test the Duplicate System

1. **Generate small batch:**
   ```
   Generate 4 QR codes
   → Should create 8 tags (4×2)
   → Should fit on 1 page
   ```

2. **Preview:**
   ```
   Check layout:
   - 2 columns (left = originals, right = copies)
   - 4 rows
   - Cut marks visible
   - Scissor icons present
   ```

3. **Print test page:**
   ```
   Print → Check:
   - Cut marks print clearly
   - Both tags identical
   - Easy to identify cut lines
   ```

4. **Cut test:**
   ```
   Cut along lines:
   - Vertical cut separates pairs
   - Horizontal cuts separate rows
   - Clean separation
   ```

---

## 💡 Pro Tips

### Tip 1: Cutting Efficiency
Use a paper cutter for straight, clean cuts:
1. Cut all vertical lines first (separate columns)
2. Then cut horizontal lines (separate rows)
3. Result: Perfect pairs

### Tip 2: Storage
Use small envelopes or plastic bags:
- Label with QR code
- Store original + copy together
- Easy to find when needed

### Tip 3: Distribution
When giving to customer:
1. Cut the pair
2. Give original to customer
3. File copy with customer details
4. Easy tracking

### Tip 4: Quality Check
Before cutting:
- Scan both QR codes
- Verify they work
- Check category indicator
- Then cut and distribute

---

## 🚀 Deployment

### Already Deployed
The feature is in the code. Just:

1. **Refresh preview page** to see duplicates
2. **Print** - cut marks will appear
3. **Cut along lines** - separate tags

### No Changes Needed
- ✅ Database - No changes
- ✅ QR generation - Same as before
- ✅ Activation - Works the same
- ✅ Only printing layout changed

---

## 📞 Support

### Common Questions

**Q: Can I print without duplicates?**
A: Currently no, but you can just use the left column (originals) and discard the right column (copies).

**Q: Do both tags work the same?**
A: Yes! They're identical - same QR code, same functionality.

**Q: What if I only need originals?**
A: Just cut and use the left column, keep or discard the right column.

**Q: Can I change the layout?**
A: Yes, edit the template to adjust columns/rows or remove duplication.

---

## ✅ Summary

**What changed:**
- ✅ Each QR printed twice (original + copy)
- ✅ Cut marks added (dashed lines + scissors)
- ✅ Same page layout (2×4 = 8 tags)
- ✅ 4 unique QRs per page (instead of 8)

**Benefits:**
- ✅ Backup copies for records
- ✅ Easy cutting with guides
- ✅ Professional appearance
- ✅ Better inventory management

**Usage:**
- ✅ Generate batch as usual
- ✅ Preview shows duplicates
- ✅ Print with cut marks
- ✅ Cut and distribute

---

**Last Updated:** January 23, 2026
**Status:** ✅ Complete and Ready to Use
