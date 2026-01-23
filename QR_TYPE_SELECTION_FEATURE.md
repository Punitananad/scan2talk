# QR Type Selection Feature

## Overview
Added the ability to choose between **Single** or **Pair** QR generation when creating QR code batches.

## Feature Details

### QR Types

1. **Single QR**
   - Generates 1 QR code per vehicle
   - Ideal for: Single-sided tags, simple deployments
   - Example: 10 vehicles = 10 QR codes

2. **Pair QR**
   - Generates 2 QR codes per vehicle
   - Ideal for: Front & back tags, dual-sided deployments
   - Example: 10 vehicles = 20 QR codes (2 per vehicle)

## How It Works

### User Interface
- **Location**: QR Generation page (`/gqr/`)
- **Selection**: Radio buttons for Single/Pair choice
- **Dynamic Help**: Quantity field shows real-time calculation
  - Single: "10 vehicles (10 QR codes will be generated)"
  - Pair: "10 vehicles (20 QR codes will be generated - 2 per vehicle)"

### Backend Logic
1. User enters **quantity** = number of vehicles
2. System calculates actual QR codes to generate:
   - Single: `qr_codes = quantity`
   - Pair: `qr_codes = quantity × 2`
3. Batch notes automatically include QR type info
4. Success message shows both vehicle count and QR count

### Example Usage

**Single QR Generation:**
```
Quantity: 50 vehicles
QR Type: Single
Result: 50 QR codes generated
Batch Notes: "[QR Type: SINGLE - 50 vehicles]"
```

**Pair QR Generation:**
```
Quantity: 50 vehicles
QR Type: Pair
Result: 100 QR codes generated (2 per vehicle)
Batch Notes: "[QR Type: PAIR - 50 vehicles]"
```

## Files Modified

### 1. Template: `templates/gateways/generate_qr.html`
- Added QR type radio button selection
- Added dynamic quantity help text
- Added JavaScript to update help text in real-time

### 2. View: `apps/gateways/qr_views.py`
- Modified `generate_qr_codes()` function
- Added `qr_type` parameter handling
- Updated QR generation logic to multiply by 2 for pairs
- Enhanced success messages with vehicle and QR counts
- Auto-appends QR type info to batch notes

## Benefits

1. **Flexibility**: Choose the right QR deployment strategy
2. **Clarity**: Clear indication of how many QR codes will be generated
3. **Tracking**: Batch notes automatically record QR type
4. **User-Friendly**: Real-time feedback on quantity calculations

## Usage Tips

- **Single QR**: Best for vehicles with one visible surface
- **Pair QR**: Best for vehicles needing front and back tags
- **Batch Notes**: QR type is automatically recorded for reference
- **Printing**: Both QRs in a pair are independent and can be printed separately

## Technical Notes

- Default selection: Single QR
- Quantity limit: 1-1000 vehicles (max 2000 QR codes for pairs)
- Each QR code is unique and independent
- Both QRs in a pair can be activated separately (they're not linked)
- Category assignment applies to all QR codes in the batch

## Future Enhancements (Optional)

- Link paired QR codes together in the database
- Show pair relationships in QR dashboard
- Generate paired QR codes on same PDF page
- Add "Front" and "Back" labels to paired QRs
