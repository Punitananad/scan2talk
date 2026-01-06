# Quick Start Guide - Vehicle QR Code System

## 🚀 Your System is Ready!

The vehicle QR code system has been successfully implemented. Here's how to use it:

## Step 1: Start the Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Step 2: Access Admin Panel

1. Go to: http://localhost:8000/admin/
2. Login with:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: (set your password with `python manage.py changepassword admin`)

## Step 3: Generate QR Codes

### Option A: Via Web Interface (Recommended)
1. Visit: http://localhost:8000/gateways/gqr/
2. Enter quantity (e.g., 10)
3. Add purpose (optional): "Test batch for parking"
4. Click "Generate QR Codes"
5. Success! QR codes are created

### Option B: Via Django Admin
1. Go to: http://localhost:8000/admin/gateways/pregeneratedqr/
2. Click "Add Pre Generated QR"
3. Save (code auto-generates)

## Step 4: View QR Dashboard

Visit: http://localhost:8000/gateways/qr/dashboard/

You'll see:
- Total QR codes
- Available, Reserved, Activated counts
- Table with all QR codes
- Filters by status and batch
- Search functionality

## Step 5: Test QR Activation

### Create a Test User First
```bash
python manage.py createsuperuser
# Or create via /admin/accounts/user/add/
```

### Activate a QR Code
1. From dashboard, note a QR code (e.g., `ABC12XYZ`)
2. Visit: http://localhost:8000/gateways/activate/ABC12XYZ/
3. Login with your user account
4. Fill in vehicle details:
   - Vehicle Type: Car
   - Vehicle Number: TEST-1234
   - Vehicle Model: Test Vehicle
5. Click "Activate QR Code"
6. Success! QR is now linked to your vehicle

## Step 6: Test Public Access

Visit: http://localhost:8000/gateways/g/ABC12XYZ/

- If activated: Shows contact form (to be implemented)
- If not activated: Shows activation prompt

## 📋 Available Routes

### Admin Routes (Staff Only)
- `/gateways/gqr/` - Generate QR codes
- `/gateways/qr/dashboard/` - QR dashboard
- `/admin/gateways/pregeneratedqr/` - Django admin

### User Routes
- `/gateways/activate/<code>/` - Activate QR code
- `/gateways/g/<code>/` - Public access

### API Routes
- `POST /gateways/api/qr/generate/` - Generate batch
- `GET /gateways/api/qr/my/` - My QR codes
- `POST /gateways/api/qr/activate/<code>/` - Activate

## 🎯 Common Tasks

### Generate 100 QR Codes
```bash
# Via API
curl -X POST http://localhost:8000/gateways/api/qr/generate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100, "purpose": "Parking lot A"}'
```

### Check QR Code Status
```bash
# Via Django shell
python manage.py shell
>>> from apps.gateways.qr_models import PreGeneratedQR
>>> qr = PreGeneratedQR.objects.get(qr_code='ABC12XYZ')
>>> print(qr.status, qr.owner, qr.gateway)
```

### View All Available QR Codes
```bash
python manage.py shell
>>> from apps.gateways.qr_models import PreGeneratedQR
>>> available = PreGeneratedQR.objects.filter(status='available')
>>> for qr in available[:10]:
...     print(f"{qr.qr_code} - {qr.get_activation_url()}")
```

## 🖨️ Print QR Codes

QR images are saved in: `media/qr_codes/pregenerated/`

1. Navigate to media folder
2. Find QR images (e.g., `qr_ABC12XYZ.png`)
3. Print as stickers (recommended size: 2x2 inches)
4. Include activation URL below QR code

## 🔧 Troubleshooting

### QR Images Not Generating
```bash
# Install required packages
pip install qrcode[pil] Pillow

# Check media directory exists
mkdir -p media/qr_codes/pregenerated
```

### Can't Access Admin Routes
- Ensure user has `is_staff=True`
- Check in Django admin: /admin/accounts/user/

### Activation Fails
- Verify QR code status is "available"
- Check user is logged in
- Ensure QR code exists

## 📊 Monitor Your System

### View Statistics
```python
from apps.gateways.qr_models import PreGeneratedQR, QRBatch

# Overall stats
total = PreGeneratedQR.objects.count()
available = PreGeneratedQR.objects.filter(status='available').count()
activated = PreGeneratedQR.objects.filter(status='activated').count()

print(f"Total: {total}, Available: {available}, Activated: {activated}")

# Batch stats
for batch in QRBatch.objects.all():
    print(f"{batch.batch_number}: {batch.activated_count}/{batch.quantity} activated")
```

## 🎨 Customize

### Change QR Code Length
Edit `apps/gateways/qr_models.py`:
```python
def generate_unique_code(self):
    code = generate_short_code(12)  # Change from 8 to 12
```

### Add Custom Fields
Add to `PreGeneratedQR` model:
```python
vehicle_color = models.CharField(max_length=50, blank=True)
parking_zone = models.CharField(max_length=50, blank=True)
```

Then run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📱 Next Features to Implement

1. **Contact Form**: When someone scans activated QR
2. **SMS/WhatsApp Integration**: Send notifications to owner
3. **QR Code Download**: Bulk download as PDF
4. **Analytics Dashboard**: Track scans, activations
5. **Payment Integration**: Charge for QR codes
6. **Mobile App**: Scan and activate via app

## 🎉 You're All Set!

Your vehicle QR code system is fully functional. Start by:
1. Generating a test batch of 10 QR codes
2. Activating one for your test vehicle
3. Testing the public access flow
4. Customizing templates to match your brand

For detailed documentation, see:
- `QR_SYSTEM_GUIDE.md` - Complete system documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details

Happy coding! 🚗💨
