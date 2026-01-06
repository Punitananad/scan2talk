# Vehicle QR Code System - Implementation Guide

## Overview
The system allows pre-generation of QR codes that users can later activate and link to their vehicles. This enables anonymous communication between vehicle owners and others without revealing personal contact information.

## System Flow

### 1. QR Code Generation (Admin)
**Route:** `/gateways/gqr/`

- Admin generates batches of QR codes
- Each QR code gets:
  - Unique identifier (e.g., `ABC12XYZ`)
  - Activation URL: `https://domain.com/gateways/activate/ABC12XYZ/`
  - Access URL: `https://domain.com/gateways/g/ABC12XYZ/`
  - QR image file
  - Activation token (for security)

### 2. QR Code Dashboard (Admin)
**Route:** `/gateways/qr/dashboard/`

- View all QR codes with filters
- See statistics (available, activated, reserved, expired)
- Manually activate QR codes for specific users
- Search and filter by status, batch, or code

### 3. User Activation
**Route:** `/gateways/activate/<qr_code>/`

When a user scans or visits the activation URL:
1. System checks if QR code is available
2. User logs in (if not already)
3. User fills in vehicle details:
   - Vehicle type (car, bike, truck, etc.)
   - License plate number
   - Vehicle make/model (optional)
4. System creates a Gateway linked to the QR code
5. QR code status changes to "activated"

### 4. Public Access
**Route:** `/gateways/g/<qr_code>/`

When someone scans an activated QR code:
- If not activated: Shows activation page
- If activated: Shows contact form to reach vehicle owner
- Owner's phone number remains hidden
- Messages routed through the platform

## Database Models

### PreGeneratedQR
- `qr_code`: Unique identifier (8 chars)
- `status`: available, reserved, activated, expired, disabled
- `owner`: User who activated it (nullable)
- `gateway`: Linked gateway (nullable)
- `activation_token`: Security token
- `batch_number`: For tracking batches
- `access_count`: How many times scanned
- `qr_image`: Generated QR code image

### QRBatch
- `batch_number`: Unique batch identifier
- `quantity`: Number of QR codes in batch
- `purpose`: Why this batch was created
- `activated_count`, `reserved_count`, `available_count`: Statistics

## API Endpoints

### Generate QR Batch (Admin Only)
```
POST /gateways/api/qr/generate/
{
  "quantity": 10,
  "purpose": "Parking lot A",
  "notes": "For new building"
}
```

### Get My QR Codes (Authenticated)
```
GET /gateways/api/qr/my/
```

### Activate QR Code (Authenticated)
```
POST /gateways/api/qr/activate/<qr_code>/
{
  "vehicle_type": "car",
  "vehicle_number": "ABC-1234",
  "vehicle_model": "Toyota Camry 2020"
}
```

## Admin Features

### Django Admin
Access at `/admin/gateways/`

**PreGeneratedQR Admin:**
- View QR code image preview
- See activation and access URLs
- Filter by status, batch, date
- Bulk actions: mark as available, mark as expired
- Search by QR code or owner email

**QRBatch Admin:**
- View batch statistics
- Update statistics action
- Filter by creation date

### Manual Activation
Admin can activate a QR code for a specific user:
1. Go to QR Dashboard
2. Find available QR code
3. Click "Activate"
4. Enter user UUID
5. System creates gateway and activates QR

## Usage Examples

### Example 1: Generate 100 QR Codes
1. Admin visits `/gateways/gqr/`
2. Enters quantity: 100
3. Purpose: "Vehicle QR codes for Mall parking"
4. Clicks "Generate QR Codes"
5. System creates batch with 100 unique QR codes
6. Admin can download/print QR codes

### Example 2: User Activates QR Code
1. User receives QR sticker with code `XYZ789AB`
2. User scans QR or visits `/gateways/activate/XYZ789AB/`
3. Logs in to their account
4. Fills vehicle details:
   - Type: Car
   - Number: DL-01-AB-1234
   - Model: Honda City 2022
5. Clicks "Activate QR Code"
6. QR code now linked to their vehicle

### Example 3: Someone Contacts Vehicle Owner
1. Person sees car with lights on
2. Scans QR code on windshield
3. Visits `/gateways/g/XYZ789AB/`
4. Sees contact form
5. Selects reason: "Lights left on"
6. Writes message: "Your headlights are still on"
7. Submits form
8. Owner receives SMS/WhatsApp notification
9. Owner's phone number never revealed

## Security Features

1. **Activation Token**: Each QR has unique token to prevent unauthorized activation
2. **Status Checks**: Only "available" QR codes can be activated
3. **Owner Verification**: User must be logged in to activate
4. **Access Logging**: All QR scans are tracked
5. **Rate Limiting**: Prevents spam through middleware

## Configuration

### Settings Required
```python
PLATFORM_DOMAIN = 'yourdomain.com'  # For QR code URLs
MEDIA_ROOT = BASE_DIR / 'media'     # For QR images
MEDIA_URL = '/media/'
```

### Permissions
- QR Generation: Staff/Admin only
- QR Dashboard: Staff/Admin only
- QR Activation: Authenticated users
- Public Access: Anyone (no auth required)

## Next Steps

1. **Print QR Codes**: Export QR images and print as stickers
2. **Distribute**: Give/sell QR stickers to vehicle owners
3. **Monitor**: Use dashboard to track activation rates
4. **Support**: Help users activate their QR codes
5. **Scale**: Generate more batches as needed

## Troubleshooting

**QR code not generating image:**
- Check MEDIA_ROOT and MEDIA_URL settings
- Ensure `qrcode` and `Pillow` packages installed
- Check file permissions on media directory

**Activation fails:**
- Verify QR code status is "available"
- Check user is authenticated
- Ensure gateway creation permissions

**Dashboard not accessible:**
- Verify user has staff/admin permissions
- Check URL routing in urls.py
- Ensure templates exist in templates/gateways/
