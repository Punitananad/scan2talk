# Distributor OTP-Based Login System

## Overview
Changed distributor login from password-based to OTP-based authentication for better security and ease of use.

## Changes Made

### 1. Backend Logic (`apps/accounts/distributor_views.py`)

**Old Flow:**
- Enter mobile number + password
- Authenticate with Django auth system
- Login if credentials match

**New Flow:**
- **Step 1**: Enter mobile number → Send OTP
- **Step 2**: Verify OTP → Auto-login

### 2. Two-Step Authentication Process

#### Step 1: Mobile Number Entry
```python
# User enters mobile number
# System validates:
- 10-digit phone number
- Distributor exists with this phone
- Distributor is verified by admin
# If valid → Send OTP
```

#### Step 2: OTP Verification
```python
# User enters OTP
# System verifies OTP
# If valid → Auto-login user
# Session maintained
```

### 3. Template Updates (`templates/accounts/distributor_login.html`)

**Step 1 Screen:**
- Mobile number input field
- "Send OTP" button
- Clean, modern UI with purple gradient

**Step 2 Screen:**
- OTP input field (6 digits)
- "Verify & Login" button
- "Resend OTP" option
- "Use different number" link

## Key Features

### Security
- ✅ No password storage needed
- ✅ OTP expires after use
- ✅ Rate limiting on OTP requests
- ✅ Session-based authentication

### User Experience
- ✅ No need to remember passwords
- ✅ Quick 2-step login
- ✅ Resend OTP option
- ✅ Clear error messages
- ✅ Mobile-friendly design

### Session Management
- Phone number stored in session during OTP flow
- User ID stored to prevent phone number spoofing
- Session cleared after successful login
- Automatic redirect if already logged in

## Technical Implementation

### OTP Service Integration
Uses existing `apps/accounts/phone_auth.py`:
- `send_otp(phone)` - Sends OTP via SMS
- `verify_otp(phone, otp)` - Verifies OTP code

### Authentication Flow
```python
1. User enters phone → send_otp()
2. Store phone + user_id in session
3. User enters OTP → verify_otp()
4. If valid → login(request, user)
5. Clear session → redirect to dashboard
```

### Debug Logging
Comprehensive logging for troubleshooting:
```python
print(f"🔐 DISTRIBUTOR LOGIN - STEP 1")
print(f"   Phone entered: {phone_digits}")
print(f"   ✓ DISTRIBUTOR FOUND: {u.email}")
print(f"📤 Sending OTP to {phone_digits}...")
```

## User Flow Diagram

```
┌─────────────────────────────────────┐
│  Distributor clicks "Login"         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 1: Enter Mobile Number        │
│  ┌─────────────────────────────┐   │
│  │ [__________] 10-digit phone │   │
│  │ [Send OTP]                  │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  System validates & sends OTP       │
│  - Check if distributor exists      │
│  - Check if verified by admin       │
│  - Send OTP via SMS                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 2: Enter OTP                  │
│  ┌─────────────────────────────┐   │
│  │ [______] 6-digit OTP        │   │
│  │ [Verify & Login]            │   │
│  │ [Resend OTP]                │   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  System verifies OTP                │
│  - Validate OTP code                │
│  - Auto-login user                  │
│  - Redirect to dashboard            │
└─────────────────────────────────────┘
```

## Error Handling

### Common Errors & Messages

1. **Phone not found**
   - Message: "No verified distributor account found with this phone number"
   - Action: Check phone number or contact admin

2. **Not verified by admin**
   - Message: "Your distributor account is pending admin verification"
   - Action: Wait for admin approval

3. **OTP send failed**
   - Message: "Failed to send OTP: [reason]"
   - Action: Check SMS service or try again

4. **Invalid OTP**
   - Message: "Invalid or expired OTP"
   - Action: Request new OTP

5. **Session expired**
   - Message: "Session expired. Please start again."
   - Action: Return to step 1

## Testing

### Test Scenarios

1. **Happy Path**
   ```
   1. Enter valid distributor phone
   2. Receive OTP
   3. Enter correct OTP
   4. Successfully login
   ```

2. **Invalid Phone**
   ```
   1. Enter non-distributor phone
   2. See error message
   3. Cannot proceed
   ```

3. **Unverified Distributor**
   ```
   1. Enter unverified distributor phone
   2. See "pending verification" message
   3. Cannot login
   ```

4. **Wrong OTP**
   ```
   1. Enter valid phone
   2. Receive OTP
   3. Enter wrong OTP
   4. See error, can retry
   ```

5. **Resend OTP**
   ```
   1. Enter valid phone
   2. Receive OTP
   3. Click "Resend OTP"
   4. Receive new OTP
   5. Enter new OTP
   6. Successfully login
   ```

## Benefits Over Password System

### For Distributors
- ✅ No password to remember
- ✅ Faster login process
- ✅ More secure (OTP expires)
- ✅ No password reset needed

### For Admin
- ✅ No password management
- ✅ No password reset requests
- ✅ Better security
- ✅ Easier onboarding

### For System
- ✅ Reduced support tickets
- ✅ Better security posture
- ✅ Simpler user management
- ✅ Consistent with user login flow

## Configuration

### OTP Settings
Located in `apps/accounts/phone_auth.py`:
- OTP length: 6 digits
- OTP expiry: 10 minutes
- Rate limiting: Configurable
- SMS provider: SMSCountry (configurable)

### Session Settings
- Session key: `distributor_login_phone`
- Session key: `distributor_user_id`
- Auto-clear after login
- Expires with browser session

## Migration Notes

### Existing Distributors
- No action needed
- Old passwords are ignored
- OTP system works immediately
- No data migration required

### Admin Panel
- No changes to admin verification process
- Password field no longer used for distributors
- Phone number remains primary identifier

## Future Enhancements (Optional)

1. **Remember Device**
   - Skip OTP on trusted devices
   - 30-day device token

2. **Biometric Login**
   - Fingerprint/Face ID on mobile
   - Fallback to OTP

3. **Email OTP Option**
   - Alternative to SMS
   - For areas with poor SMS delivery

4. **Login History**
   - Track login attempts
   - Show last login time
   - Security alerts

## Related Files

- `apps/accounts/distributor_views.py` - Login logic
- `templates/accounts/distributor_login.html` - Login UI
- `apps/accounts/phone_auth.py` - OTP service
- `apps/communications/otp_service.py` - SMS delivery
