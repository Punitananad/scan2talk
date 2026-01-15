# 🎯 QR Position Adjustment Guide

## How to Edit QR Coordinates Yourself

### File to Edit
Open: `apps/gateways/qr_download_views.py`

### Find These Lines (appears TWICE in the file)

Look for these coordinates:
```python
QR_SIZE = 420  # QR code size in pixels
QR_X = 850     # Horizontal position (left edge)
QR_Y = 180     # Vertical position (top edge)
```

### How to Adjust

#### Move QR LEFT/RIGHT (X coordinate)
- **Move LEFT**: Decrease QR_X (e.g., 850 → 840)
- **Move RIGHT**: Increase QR_X (e.g., 850 → 860)

#### Move QR UP/DOWN (Y coordinate)
- **Move UP**: Decrease QR_Y (e.g., 180 → 170)
- **Move DOWN**: Increase QR_Y (e.g., 180 → 190)

#### Change QR SIZE
- **Make BIGGER**: Increase QR_SIZE (e.g., 420 → 440)
- **Make SMALLER**: Decrease QR_SIZE (e.g., 420 → 400)

### Example Adjustments

```python
# Current position
QR_X = 850
QR_Y = 180

# Move 10 pixels left and 5 pixels up
QR_X = 840  # 850 - 10
QR_Y = 175  # 180 - 5

# Move 15 pixels right and 10 pixels down
QR_X = 865  # 850 + 15
QR_Y = 190  # 180 + 10
```

### Where to Change (2 locations)

#### Location 1: `preview_batch_sample` function
Around line 60-65:
```python
# FIXED COORDINATES for RIGHT-side yellow box
QR_SIZE = 420
QR_X = 850
QR_Y = 180
```

#### Location 2: `download_batch_pdf` function
Around line 140-145:
```python
# FIXED COORDINATES for RIGHT-side yellow box
QR_SIZE = 420
QR_X = 850
QR_Y = 180
```

**IMPORTANT**: Change BOTH locations to keep preview and PDF consistent!

### Testing Your Changes

1. Save the file after editing
2. Refresh your preview page in browser
3. Check if QR is positioned correctly
4. Adjust again if needed

### Quick Reference

| Action | Change | Example |
|--------|--------|---------|
| Move left | QR_X - 10 | 850 → 840 |
| Move right | QR_X + 10 | 850 → 860 |
| Move up | QR_Y - 10 | 180 → 170 |
| Move down | QR_Y + 10 | 180 → 190 |
| Bigger QR | QR_SIZE + 20 | 420 → 440 |
| Smaller QR | QR_SIZE - 20 | 420 → 400 |

### Template Reference

- Template size: 1421 x 768 pixels
- Yellow box area: X(786-1359), Y(0-757)
- Current QR: 420x420 at position (850, 180)

### Tips

- Make small changes (5-20 pixels at a time)
- Always change BOTH locations in the file
- Refresh browser to see changes
- Keep QR inside yellow box boundaries

---

**Current Coordinates**: X=850, Y=180, Size=420
