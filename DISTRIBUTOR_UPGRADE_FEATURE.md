# Distributor Upgrade Feature

## Overview
Existing users (tag owners) can now upgrade their accounts to become distributors. Users and distributors are NOT mutually exclusive - a person can be BOTH a tag owner AND a distributor.

## Problem Fixed
Previously, the system blocked existing users from registering as distributors with the error:
```
"This phone number is already registered"
```

This was incorrect because:
- Users and distributors are two different roles
- A user can have BOTH roles simultaneously
- The system should allow existing users to UPGRADE to distributor status

## Solution Implemented

### Step 1: Phone Number Check (Modified)
The registration flow now distinguishes between three scenarios:

1. **Phone exists AND user is already a distributor** → Block registration
   - Error: "This phone number is already registered as a distributor"
   
2. **Phone exists BUT user is NOT a distributor** → Allow upgrade
   - System stores existing user ID in session
   - User proceeds to OTP verification
   - After OTP, existing account is upgraded to distributor
   
3. **Phone doesn't exist** → Create new user as distributor
   - Standard new user creation flow

### Step 2: OTP Verification & Account Creation/Upgrade (Modified)
After successful OTP verification, the system checks if this is an upgrade or new registration:

#### Existing User Upgrade Path:
```python
if existing_user_id:
    # Get existing user
    user = User.objects.get(id=existing_user_id)
    
    # Upgrade to distributor
    user.is_distributor = True
    user.distributor_verified = False  # Pending admin approval
    user.distributor_registered_at = now()
    
    # Update name if provided
    user.first_name = name
    
    # Update email if provided and available
    if email and email != user.email:
        user.email = email
    
    # Store bank details
    user.last_name = json.dumps(bank_details)
    
    user.save()
```

#### New User Creation Path:
```python
else:
    # Create new distributor account
    user = User.objects.create(
        username=f"dist_{phone[-4:]}_{uuid}",
        email=email or f"{username}@distributor.local",
        first_name=name,
        phone=encrypt_data(phone),
        is_phone_verified=True,
        is_distributor=True,
        distributor_verified=False,
        distributor_registered_at=now()
    )
    
    # Store bank details
    user.last_name = json.dumps(bank_details)
    
    # Set unusable password (OTP login only)
    user.set_unusable_password()
    user.save()
```

## User Experience

### Scenario 1: New User Registering as Distributor
1. Visit `/accounts/distributor/register/`
2. Enter details (name, phone, email, bank details)
3. Receive OTP
4. Verify OTP
5. New account created as distributor (pending admin approval)

### Scenario 2: Existing User Upgrading to Distributor
1. Visit `/accounts/distributor/register/`
2. Enter details with SAME phone number as existing account
3. System detects existing user (no error shown)
4. Receive OTP
5. Verify OTP
6. Existing account upgraded to distributor (pending admin approval)
7. User retains all existing data (gateways, payments, etc.)

## Technical Details

### Files Modified
- `apps/accounts/distributor_views.py`
  - `distributor_register()` function
  - Lines 54-72: Phone number check logic
  - Lines 140-220: Account creation/upgrade logic

### Session Variables
- `dist_reg_existing_user_id`: Stores existing user ID if upgrading (Step 1 → Step 2)
- Cleared after successful registration/upgrade

### Database Changes
When upgrading existing user:
- `is_distributor` → `True`
- `distributor_verified` → `False` (admin approval required)
- `distributor_registered_at` → Current timestamp
- `first_name` → Updated if provided
- `email` → Updated if provided and available
- `last_name` → Bank details JSON

## Admin Workflow
After user registers/upgrades to distributor:
1. Admin receives notification (pending approval)
2. Admin reviews distributor details in admin panel
3. Admin sets:
   - `distributor_verified` → `True`
   - `distributor_total_qr` → Number of QR codes assigned
   - `distributor_commission_per_activation` → Commission amount
4. Distributor can now login and access dashboard

## Benefits
✅ Existing users can become distributors without creating new accounts
✅ Users retain all existing data (gateways, payments, history)
✅ Single phone number for both user and distributor roles
✅ Simplified user experience
✅ No duplicate accounts

## Testing

### Test Case 1: New User Registration
```bash
# Register new distributor
Phone: 9999999999 (not in system)
Expected: New account created
```

### Test Case 2: Existing User Upgrade
```bash
# Register existing user as distributor
Phone: 9876543210 (already exists as user)
Expected: Account upgraded to distributor
```

### Test Case 3: Existing Distributor
```bash
# Try to register again
Phone: 9876543210 (already a distributor)
Expected: Error - "This phone number is already registered as a distributor"
```

## Debug Output
The system logs detailed information during registration:

```
============================================================
📝 DISTRIBUTOR REGISTRATION - STEP 1
   Name: John Doe
   Email: john@example.com
   Phone: 9876543210
   ℹ️  EXISTING USER FOUND - Will upgrade to distributor
   User ID: abc-123-def
   Email: john@example.com
============================================================

============================================================
⬆️  UPGRADING EXISTING USER TO DISTRIBUTOR
============================================================

✅ USER UPGRADED TO DISTRIBUTOR
   User ID: abc-123-def
   Email: john@example.com
   Phone: 9876543210
   Bank Details: {...}
```

## Related Documentation
- `DISTRIBUTOR_REGISTRATION_SYSTEM.md` - Original registration system
- `DISTRIBUTOR_COMMISSION_ON_PAYMENT.md` - Commission tracking
- `PHONE_LOGIN_SYSTEM.md` - OTP authentication

---

**Date**: January 25, 2026
**Status**: ✅ Implemented and Tested
**Version**: 1.0
