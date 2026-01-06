# Access Count & Owner Name Update

## Changes Made

### 1. Owner Name Field Added ✅

**What Changed:**
- Added `owner_name` field to the `Gateway` model
- This field stores the owner's name entered during QR activation
- The name is now displayed in the dashboard instead of just email

**Files Modified:**
- `apps/gateways/models.py` - Added `owner_name` field
- `apps/gateways/qr_views.py` - Updated to save owner name during activation
- `templates/gateways/qr_dashboard.html` - Shows owner name in dashboard
- `templates/gateways/qr_already_activated.html` - Uses owner name from gateway

**Migration Created:**
- `apps/gateways/migrations/0003_gateway_owner_name.py`

### 2. Access Count Clarification

**What Access Count Tracks:**
The `access_count` field in the `PreGeneratedQR` model tracks:
- Every time someone scans the QR code
- Every time someone visits the activation URL
- Every time someone accesses the gateway through that QR code

**Important Notes:**
- ✅ QR can only be **activated once** by the owner
- ✅ QR can be **accessed multiple times** by different people to contact the owner
- ✅ Access count increments on every scan/visit (not just activation)

**Where It's Used:**
```python
# In qr_views.py - activate_qr_code() function
qr.increment_access_count()  # Called every time QR is accessed

# In qr_views.py - public_qr_access() function
qr.increment_access_count()  # Called when people contact the owner
```

### 3. Activation Flow

**Step 1: Phone Number**
- User enters their phone number
- OTP is sent

**Step 2: OTP Verification**
- User enters OTP code
- Phone is verified

**Step 3: Details (NOW INCLUDES NAME)**
- ✅ **Owner Name** (Required) - NEW!
- Vehicle Type (Required)
- Vehicle Number (Required)
- Vehicle Model (Optional)

**Step 4: Success**
- QR code is activated
- Gateway is created with owner's name
- Owner can now receive contact requests

## Database Schema

### Gateway Model
```python
class Gateway(BaseModel):
    owner = models.ForeignKey(User)
    owner_name = models.CharField(max_length=200, blank=True)  # NEW FIELD
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    context_type = models.CharField(max_length=20)
    identifier_text = models.CharField(max_length=100)  # Vehicle number
    # ... other fields
```

### PreGeneratedQR Model
```python
class PreGeneratedQR(models.Model):
    qr_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20)  # available, activated, etc.
    owner = models.ForeignKey(User)
    gateway = models.OneToOneField(Gateway)
    access_count = models.PositiveIntegerField(default=0)  # Tracks all accesses
    # ... other fields
```

## Usage Examples

### Dashboard Display
Before:
```
Owner: user@example.com
```

After:
```
Owner: John Doe
```

### Already Activated Page
Before:
```
This QR code belongs to Vehicle Owner
```

After:
```
This QR code belongs to John Doe
```

## Migration Instructions

The migration has already been applied. If you need to run it again:

```bash
python manage.py makemigrations gateways
python manage.py migrate gateways
```

## Testing

1. **Generate a new QR code:**
   - Visit: http://192.168.1.75:8000/gateways/gqr/
   - Generate 1 QR code

2. **Activate with name:**
   - Scan QR code or visit activation URL
   - Enter phone number
   - Enter OTP
   - **Enter your name** (e.g., "John Doe")
   - Enter vehicle details
   - Complete activation

3. **Verify in dashboard:**
   - Visit: http://192.168.1.75:8000/gateways/qr/dashboard/
   - Check "Owner" column shows "John Doe"

4. **Test access count:**
   - Scan the same QR code again
   - Access count should increment
   - Try accessing from different devices
   - Each access increments the counter

## Summary

✅ Owner name is now collected during activation
✅ Owner name is displayed in dashboard
✅ Access count tracks all QR scans/accesses (not just activation)
✅ QR can only be activated once but accessed multiple times
✅ Migration applied successfully
