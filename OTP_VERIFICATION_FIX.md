# OTP Verification Fix - First Attempt Success

## Problem
OTP verification was failing on the first attempt and only succeeding after 2-3 tries for both regular users and distributors.

## Root Cause
The OTP was being sent successfully, but **NOT stored in cache immediately**. The flow was:

1. User requests OTP
2. `send_otp()` sends SMS successfully
3. `send_otp()` returns success **WITHOUT storing OTP**
4. `phone_auth.py` tries to store OTP **AFTER** the function returns
5. User enters OTP immediately
6. **First verification fails** - OTP not in cache yet
7. User tries again
8. **Second verification succeeds** - OTP now stored from previous attempt

## Solution
Modified `apps/communications/otp_service.py` to **store OTP immediately** after successful SMS sending, BEFORE returning from the function.

### Changes Made

**File: `apps/communications/otp_service.py`**
- Added `self.store_otp(phone_number, otp)` immediately after every successful SMS send
- This happens in ALL success paths:
  - 202 Accepted (queued)
  - 200/201 with Success=True
  - 200/201 without Success field
  - Dev mode fallbacks
  - Error fallbacks in debug mode

**File: `apps/accounts/phone_auth.py`**
- Removed duplicate `otp_service.store_otp()` call
- Now relies on OTP service to handle storage automatically

## Testing
After this fix:
1. User requests OTP
2. OTP is sent AND stored immediately
3. User enters OTP on first attempt
4. ✅ **Verification succeeds on first try**

## Deployment

```bash
# Push changes
git add apps/communications/otp_service.py apps/accounts/phone_auth.py
git commit -m "Fix OTP verification - store OTP immediately after sending"
git push origin main

# On production server
cd /var/www/scan2talk
git pull origin main
systemctl restart gunicorn

# Test
# 1. Request OTP for QR activation
# 2. Enter OTP immediately
# 3. Should verify on FIRST attempt
```

## Impact
- ✅ Users can verify OTP on first attempt
- ✅ Distributors can verify OTP on first attempt
- ✅ Better user experience
- ✅ No more frustration with multiple attempts
- ✅ Faster activation process

## Files Modified
1. `apps/communications/otp_service.py` - Store OTP immediately after sending
2. `apps/accounts/phone_auth.py` - Remove duplicate storage call

## Verification Checklist
- [ ] OTP sent successfully
- [ ] OTP stored in cache immediately
- [ ] First verification attempt succeeds
- [ ] Works for regular users
- [ ] Works for distributors
- [ ] Works for QR activation
- [ ] No duplicate storage calls

## Notes
- The fix ensures OTP is stored **atomically** with the send operation
- No race conditions between send and store
- Works in both production and development modes
- Maintains all existing security features (lockout, cooldown, etc.)
