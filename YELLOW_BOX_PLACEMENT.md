# CRITICAL: Yellow Box QR Placement

## The Problem
QR code was being placed on the LEFT side of the template, but it MUST be placed inside the YELLOW BOX on the RIGHT side.

## Template Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR TEMPLATE IMAGE                         │
│                                                                 │
│  LEFT SIDE                           RIGHT SIDE                │
│  ┌──────────────┐                   ┌──────────────┐          │
│  │              │                   │  ╔════════╗  │          │
│  │   SCAN       │                   │  ║ YELLOW ║  │          │
│  │   Logo/Text  │                   │  ║  BOX   ║  │ ← QR HERE│
│  │              │                   │  ║ place  ║  │          │
│  │              │                   │  ║ your   ║  │          │
│  │              │                   │  ║ Qr here║  │          │
│  └──────────────┘                   │  ╚════════╝  │          │
│                                     └──────────────┘          │
│                                                                 │
│  Bottom text / branding                                        │
└─────────────────────────────────────────────────────────────────┘
```

## What Was Wrong

### BEFORE (INCORRECT):
```
QR was placed on LEFT side or CENTER:
┌─────────────────────────────────────────┐
│  ┌─────────┐                            │
│  │ ▓▓▓▓▓▓▓ │  ← WRONG! QR on left      │
│  │ ▓▓▓▓▓▓▓ │                            │
│  │ ▓▓▓▓▓▓▓ │    [Yellow Box Empty]     │
│  └─────────┘                            │
└─────────────────────────────────────────┘
```

### AFTER (CORRECT):
```
QR is placed INSIDE the yellow box on RIGHT:
┌─────────────────────────────────────────┐
│                                         │
│  [Left content]    ┌──────────────┐    │
│                    │  ┌─────────┐ │    │
│                    │  │ ▓▓▓▓▓▓▓ │ │ ✓  │
│                    │  │ ▓▓▓▓▓▓▓ │ │    │
│                    │  │ ▓▓▓▓▓▓▓ │ │    │
│                    │  └─────────┘ │    │
│                    └──────────────┘    │
└─────────────────────────────────────────┘
```

## How Detection Works

### Step 1: Detect Yellow Color
```python
# Yellow has: High Red, High Green, Low Blue
yellow_mask = (R > 200) & (G > 150) & (B < 100)
```

### Step 2: Find Yellow Box Bounds
```python
# Find the rectangular area containing yellow pixels
rmin, rmax = vertical bounds
cmin, cmax = horizontal bounds
```

### Step 3: Calculate QR Position
```python
# Center of yellow box
qr_x = (cmin + cmax) // 2
qr_y = (rmin + rmax) // 2

# Size: 85% of box (with margins)
qr_size = min(box_width, box_height) * 0.85
```

### Step 4: Place QR Centered in Box
```python
# Center the QR in the yellow box
paste_x = qr_x - (qr_size // 2)
paste_y = qr_y - (qr_size // 2)
template.paste(qr_img, (paste_x, paste_y))
```

## Fallback Positioning

If yellow detection fails:
- Position: 75% from left (RIGHT side)
- Size: 20% of template width
- Vertical: Centered

```python
qr_x = int(template_width * 0.75)  # RIGHT side
qr_y = template_height // 2         # Centered vertically
qr_size = int(template_width * 0.20)
```

## Testing

### Test Script Output:
```bash
$ python test_template_overlay.py

5️⃣  Detecting YELLOW BOX (QR placeholder)...
   ✅ YELLOW BOX DETECTED!
      Bounds: (1200, 300) to (1500, 600)
      Box size: 300x300
      Center: (1350, 450)
      QR Size: 255x255
      Position: RIGHT side of template ✓
```

### Visual Verification:
1. Run test script
2. Open `test_tag_output.png`
3. Verify QR is INSIDE the yellow box
4. Verify QR is on the RIGHT side
5. Verify equal margins around QR

## Requirements Checklist

- [x] QR code is placed INSIDE the yellow box
- [x] QR code is on the RIGHT side of template
- [x] QR code is centered horizontally in box
- [x] QR code is centered vertically in box
- [x] QR code has equal margins on all sides
- [x] QR code does NOT overlap other elements
- [x] Background remains white
- [x] Design is print-ready (high DPI)

## Files Modified

1. **apps/gateways/qr_download_views.py**
   - Changed detection from "brightest area" to "yellow color"
   - Targets RIGHT side of template (75% from left)
   - Places QR at 85% of box size (with margins)

2. **test_template_overlay.py**
   - Updated to detect yellow box
   - Shows yellow box bounds in output
   - Verifies RIGHT side placement

## Deploy and Test

```bash
# Deploy
git pull origin main
pip install -r requirements.txt
sudo systemctl restart gunicorn

# Test
python test_template_overlay.py

# Check output
open test_tag_output.png  # Mac
xdg-open test_tag_output.png  # Linux
start test_tag_output.png  # Windows

# Generate actual PDF
# Go to /gqr/ → Generate batch → Download PDF
```

## Expected Result

When you open the PDF:
- Each tag shows your full template image
- QR code is INSIDE the yellow rounded rectangle
- Yellow box is on the RIGHT side
- QR is perfectly centered in the box
- Equal white margins around QR inside box
- 8 tags per A4 page (2×4 grid)

## Troubleshooting

### QR still on wrong side?
Check logs:
```bash
sudo journalctl -u gunicorn -f | grep "YELLOW BOX"
```

Should see:
```
✅ YELLOW BOX DETECTED: bounds=(x1,y1)-(x2,y2)
✅ QR will be placed at: center=(x, y), size=...
```

### Yellow box not detected?
1. Check template has yellow color (RGB: 255, 200, 0)
2. Adjust detection threshold in code
3. Fallback will use RIGHT side positioning (75% from left)

### QR too big/small?
Adjust the size multiplier:
```python
qr_size = int(min(box_width, box_height) * 0.85)  # Change 0.85
```

---

**Status**: ✅ Fixed - QR now places in yellow box on RIGHT side  
**Last Updated**: January 15, 2026
