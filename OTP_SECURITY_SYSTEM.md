# OTP Security System - Complete Guide

## Overview

The OTP (One-Time Password) verification system now includes industry-standard security measures to prevent abuse and ensure secure phone verification.

## Security Features

### 1. **30-Second Resend Cooldown**
- Users must wait 30 seconds between OTP resend requests
- Prevents SMS flooding and abuse
- Countdown timer shown in UI
- Enforced at service level (cannot be bypassed)

### 2. **3 Verification Attempts Per OTP**
- Each OTP can be verified maximum 3 times
- After 3 wrong attempts, OTP is invalidated
- User must request a new OTP
- Prevents brute-force attacks

### 3. **2-Hour Account Lockout**
- After 3 failed verification attempts (across multiple OTPs), account is locked
- Lockout duration: 2 hours
- Prevents persistent brute-force attacks
- Clear error message shows lockout end time

### 4. **5-Minute OTP Expiry**
- Each OTP expires after 5 minutes
- Reduces window for interception attacks
- User must request new OTP after expiry

### 5. **Secure OTP Storage**
- OTPs are hashed using SHA-256 before storage
- Never stored in plain text
- Stored in cache (Redis/in-memory) with automatic expiry

## User Flow

### Step 1: Request OTP
```
User enters phone number → System sends OTP → 30-second cooldown starts
```

### Step 2: Verify OTP
```
User enters OTP → System verifies
├─ ✅ Correct → Proceed to next step
└─ ❌ Wrong → Attempts remaining shown
    ├─ Attempts left → Try again
    └─ No attempts → Request new OTP
```

### Step 3: Lockout Protection
```
3 failed verifications → Account locked for 2 hours
User sees: "Too many failed attempts. Account locked until 3:30 PM"
```

## Technical Implementation

### Cache Keys Used

```python
# OTP storage
otp_{phone_number} = {
    'otp_hash': 'sha256_hash',
    'attempts': 3,
    'created_at': 'timestamp'
}

# Resend cooldown
otp_resend_cooldown_{phone_number} = timestamp

# Failed attempts tracking
otp_failed_attempts_{phone_number} = count

# Lockout
otp_lockout_{phone_number} = True
otp_lockout_until_{phone_number} = "3:30 PM"
```

### Configuration Constants

```python
OTP_LENGTH = 6                      # 6-digit OTP
OTP_EXPIRY_MINUTES = 5              # 5 minutes validity
MAX_VERIFICATION_ATTEMPTS = 3       # 3 attempts per OTP
RESEND_COOLDOWN_SECONDS = 30        # 30 seconds between resends
LOCKOUT_DURATION_HOURS = 2          # 2 hours lockout
MAX_FAILED_ATTEMPTS = 3             # 3 total failures before lockout
```

## API Methods

### Send OTP
```python
from apps.communications.otp_service import get_otp_service

otp_service = get_otp_service()
success, otp, message = otp_service.send_otp(phone_number)

# Returns:
# - success: bool
# - otp: str (for dev mode logging)
# - message: str (error or success message)
```

### Verify OTP
```python
success, message = otp_service.verify_otp(phone_number, otp)

# Returns:
# - success: bool
# - message: str (with remaining attempts or error)
```

### Resend OTP
```python
success, message = otp_service.resend_otp(phone_number)

# Enforces 30-second cooldown
# Returns cooldown message if too soon
```

## Error Messages

### Resend Cooldown
```
"Please wait 25 seconds before requesting a new OTP."
```

### Invalid OTP
```
"Invalid OTP. 2 attempt(s) remaining."
```

### OTP Expired
```
"OTP expired or not found. Please request a new OTP."
```

### Account Locked
```
"Too many failed attempts. Account locked until 3:30 PM. Please try again later."
```

### Max Attempts Exceeded
```
"Invalid OTP. Maximum attempts exceeded. Please request a new OTP."
```

## UI Features

### Countdown Timer
- Shows 30-second countdown after OTP sent
- Disables resend button during countdown
- Auto-enables when countdown reaches 0

### Auto-Submit
- OTP form auto-submits when 6 digits entered
- Improves user experience
- Reduces friction

### Security Notice
Displays:
- OTP validity: 5 minutes
- Verification attempts: 3
- Lockout warning: 2 hours after 3 failures
- Resend cooldown: 30 seconds

## Development Mode

In DEBUG mode, OTP is printed to console even if SMS fails:

```
==================================================
📱 OTP for 9876543210: 123456
==================================================
```

This allows testing without SMS credits.

## Production Considerations

### SMS Provider: SMSCountry
- Uses AuthKey-based REST API
- DLT-compliant message templates
- Delivery tracking via MessageUUID
- Automatic retry on transient failures

### Rate Limiting
- 30-second cooldown prevents SMS flooding
- Lockout prevents persistent attacks
- Cache-based (no database writes)

### Security Best Practices
✅ OTPs hashed before storage
✅ Automatic expiry (5 minutes)
✅ Limited verification attempts (3)
✅ Account lockout (2 hours)
✅ Resend cooldown (30 seconds)
✅ No OTP in logs (production)

## Testing

### Test OTP Flow
```bash
python test_otp_system.py
```

### Test Lockout
1. Request OTP
2. Enter wrong OTP 3 times
3. Verify lockout message appears
4. Try to request new OTP → Should show lockout

### Test Resend Cooldown
1. Request OTP
2. Immediately click "Resend"
3. Should show "Please wait X seconds"
4. Wait 30 seconds
5. Resend should work

## Troubleshooting

### OTP Not Received
1. Check phone number format (10 digits)
2. Check SMS credits in SMSCountry
3. Check DLT template approval
4. Check logs for API errors
5. In dev mode, check console for OTP

### Verification Fails
1. Check OTP hasn't expired (5 minutes)
2. Check attempts remaining
3. Check if account is locked
4. Clear cache if testing: `cache.delete(f'otp_{phone}')`

### Lockout Issues
1. Check lockout cache key: `cache.get(f'otp_lockout_{phone}')`
2. Clear lockout: `cache.delete(f'otp_lockout_{phone}')`
3. Check lockout end time: `cache.get(f'otp_lockout_until_{phone}')`

## Files Modified

- `apps/communications/otp_service.py` - Core OTP logic with security
- `templates/gateways/activate_step2_otp.html` - UI with countdown timer
- `apps/gateways/qr_views.py` - Activation flow (already had resend view)
- `apps/accounts/phone_auth.py` - Phone auth helpers

## Next Steps

1. ✅ Deploy to production
2. ✅ Test OTP flow end-to-end
3. ✅ Monitor SMS delivery rates
4. ✅ Track lockout incidents
5. ✅ Adjust cooldown/lockout if needed

## Configuration Changes

To adjust security parameters, edit `apps/communications/otp_service.py`:

```python
class SMSCountryOTPService:
    OTP_EXPIRY_MINUTES = 5              # Change OTP validity
    MAX_VERIFICATION_ATTEMPTS = 3       # Change attempts per OTP
    RESEND_COOLDOWN_SECONDS = 30        # Change resend cooldown
    LOCKOUT_DURATION_HOURS = 2          # Change lockout duration
    MAX_FAILED_ATTEMPTS = 3             # Change failures before lockout
```

## Support

For issues or questions:
1. Check logs: `/var/www/scan2talk/logs/django.log`
2. Check cache: Use Django shell to inspect cache keys
3. Test in dev mode: Set `DEBUG=True` to see OTP in console
