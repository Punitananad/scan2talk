# Distributor Registration System - Quick Start

## Overview
Standalone distributor registration system that allows anyone to register as a distributor without needing to login as a regular user first.

## Features
✅ **No Login Required** - Direct registration without user account
✅ **OTP Verification** - Two-step mobile number verification
✅ **Bank Details Collection** - For payment processing
✅ **Admin Approval** - Accounts pending admin verification
✅ **Business Name Removed** - Simplified registration (per user request)

## Registration Flow

### Step 1: Enter Details
User provides:
- Full Name (required)
- Mobile Number (required) - 10 digits
- Email (optional)
- Account Holder Name (required)
- Bank Account Number (required) - 9-18 digits
- IFSC Code (required) - 11 characters

### Step 2: OTP Verification
- OTP sent to mobile number
- User enters 6-digit OTP
- Option to resend OTP
- Account created upon successful verification

### Step 3: Pending Approval
- Account created with `distributor_verified=False`
- User shown pending approval page
- Admin must approve before distributor can login

## Technical Details

### URL Routes
```
/accounts/distributor/register/          - Registration form (step 1)
/accounts/distributor/register/?step=2   - OTP verification (step 2)
/accounts/distributor/pending/public/    - Pending approval page
```

### Data Storage
- **User Model Fields:**
  - `username`: Auto-generated as `dist_{last4digits}_{random6}`
  - `first_name`: Full name
  - `email`: Email or auto-generated
  - `phone`: Encrypted mobile number
  - `is_phone_verified`: True after OTP
  - `is_distributor`: True
  - `distributor_verified`: False (pending admin)
  - `distributor_registered_at`: Registration timestamp
  - `last_name`: JSON string with bank details (temporary storage)

- **Bank Details JSON Structure:**
```json
{
    "account_holder_name": "John Doe",
    "account_number": "1234567890",
    "ifsc_code": "SBIN0001234"
}
```

### Session Variables (Step 1 → Step 2)
- `dist_reg_name`
- `dist_reg_email`
- `dist_reg_phone`
- `dist_reg_account_holder`
- `dist_reg_account_number`
- `dist_reg_ifsc`

## Access Points

### Navigation Bar
- "Distributor Login" button visible when user NOT logged in
- Purple-themed to distinguish from regular login

### Homepage
- "Distributor Login" link in hero section
- Visible to all visitors

### Registration Page
- "Register here" link on distributor login page
- Direct access via URL

## Admin Actions Required

After registration, admin must:
1. Review distributor details in admin panel
2. Verify bank account information
3. Set `distributor_verified=True`
4. Distributor can then login with OTP

## Files Modified

### Backend
- `apps/accounts/distributor_views.py` - Registration logic
- `apps/accounts/urls.py` - URL routing

### Templates
- `templates/accounts/distributor_register.html` - Registration form
- `templates/accounts/distributor_pending_public.html` - Pending page
- `templates/accounts/distributor_login.html` - Login page
- `templates/base.html` - Navigation bar
- `templates/core/home_new.html` - Homepage link

## Testing

### Test Registration Flow
1. Go to `/accounts/distributor/register/`
2. Fill in all required fields
3. Click "Send OTP"
4. Enter OTP received
5. Verify account created with pending status

### Verify Data Storage
```python
from apps.accounts.models import User
import json

# Find the distributor
user = User.objects.filter(is_distributor=True).last()

# Check details
print(f"Name: {user.first_name}")
print(f"Phone: {user.get_decrypted_phone()}")
print(f"Verified: {user.distributor_verified}")

# Check bank details
bank_details = json.loads(user.last_name)
print(f"Bank Details: {bank_details}")
```

## Security Features

- Phone number encryption
- OTP verification required
- Session-based data transfer
- Admin approval required
- Unusable password (OTP login only)

## User Experience

### Benefits Shown
- Earn commission on QR sales
- Manage QR inventory
- Track sales and revenue
- Admin approval within 24 hours

### Clear Navigation
- Link to login if already registered
- Back to home option
- Step indicators
- Helpful error messages

## Next Steps

After admin approval:
1. Distributor can login via OTP
2. Access distributor dashboard
3. View assigned QR codes
4. Track payments and revenue

## Notes

- Business Name field was removed per user request
- Bank details stored temporarily in `last_name` field
- Consider creating separate BankDetails model in future
- OTP uses existing SMS service credentials
