# OTP Verification Issue - "OTP expired or not found"

## Problem
User enters correct OTP but gets error: "OTP expired or not found. Please request a new OTP."

## Root Cause Analysis

### Possible Causes:
1. **OTP not being stored in cache** after sending
2. **Cache expiring too quickly** (5 minutes)
3. **Phone number mismatch** between send and verify
4. **Multiple OTP requests** overwriting previous OTP
5. **Cache backend issue** (Redis/Memcached not working)

## Diagnostic Steps

### Step 1: Check Console Output
When you send OTP, look for these lines in console:
```
============================================================
📤 SEND OTP RESULT
   Phone: 9876543210
   Success: True
   OTP: 123456
   Message: OTP sent successfully
============================================================

✅ OTP stored in cache for 9876543210
✅ Verified: OTP is in cache with 3 attempts
```

If you see "❌ WARNING: OTP not found in cache after storing!" - that's the problem!

### Step 2: Check Verification Output
When you enter OTP, look for:
```
============================================================
🔐 VERIFY OTP
   Phone: 9876543210
   OTP Entered: '123456' (length: 6)
   Cache Key: otp_9876543210
   OTP in Cache: YES
   Attempts Remaining: 3
   Created At: 2026-01-23T...
============================================================
```

If "OTP in Cache: NO" - the OTP was never stored or expired!

### Step 3: Use Debug Script
```bash
# Check cache status
python test_distributor_otp_debug.py check 9876543210

# Clear cache and try again
python test_distributor_otp_debug.py clear 9876543210

# Test complete flow
python test_distributor_otp_debug.py test 9876543210
```

## Fixes Applied

### 1. Enhanced Logging in phone_auth.py
- Added detailed logging for send_otp
- Added cache verification after storing
- Added detailed logging for verify_otp
- Shows cache status before verification

### 2. Cache Verification
- Immediately check if OTP was stored after calling store_otp
- Warn if OTP not found in cache
- Show attempts remaining

### 3. Debug Information
- Show exact OTP entered (with quotes to see whitespace)
- Show OTP length
- Show cache key being used
- Show cache data structure

## Common Issues & Solutions

### Issue 1: Cache Not Working
**Symptom**: "❌ WARNING: OTP not found in cache after storing!"

**Solution**:
```python
# Check Django cache settings
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> print(cache.get('test'))
# Should print: value
```

If this doesn't work, your cache backend isn't configured properly.

### Issue 2: Phone Number Mismatch
**Symptom**: Different phone numbers in send vs verify logs

**Solution**: Ensure phone number is consistently formatted (10 digits, no spaces)

### Issue 3: OTP Expired
**Symptom**: "OTP expired or not found" after 5+ minutes

**Solution**: Request new OTP (OTPs expire after 5 minutes)

### Issue 4: Multiple Requests
**Symptom**: Sending OTP multiple times quickly

**Solution**: Wait 30 seconds between OTP requests (cooldown period)

### Issue 5: Account Locked
**Symptom**: "Too many failed attempts"

**Solution**: 
```bash
# Clear lockout
python test_distributor_otp_debug.py clear 9876543210
```

## Testing Instructions

### Test 1: Send and Verify Immediately
1. Go to distributor registration
2. Fill form and click "Send OTP"
3. **Check console immediately** - note the OTP
4. Enter OTP within 1 minute
5. Should work ✅

### Test 2: Check Cache Status
```bash
# After sending OTP
python test_distributor_otp_debug.py check 9876543210
```

Expected output:
```
✅ OTP Cache Found:
   Key: otp_9876543210
   Attempts: 3
   Created: 2026-01-23T12:34:56
   Hash: abc123...
```

### Test 3: Complete Flow Test
```bash
python test_distributor_otp_debug.py test 9876543210
```

This will:
1. Send OTP
2. Check cache
3. Ask you to enter OTP
4. Verify OTP
5. Show results

## Quick Fix for Immediate Testing

If OTP verification keeps failing, temporarily bypass it for testing:

```python
# In apps/accounts/phone_auth.py - TEMPORARY ONLY!
def verify_otp(phone_number, otp):
    # TEMPORARY: Always return success for testing
    if settings.DEBUG:
        print(f"⚠️  DEBUG MODE: Bypassing OTP verification")
        return True, "OTP verified (debug mode)"
    
    # Normal verification code...
```

**WARNING**: Remove this before production!

## Files Modified

1. `apps/accounts/phone_auth.py`
   - Enhanced send_otp logging
   - Added cache verification
   - Enhanced verify_otp logging

2. `test_distributor_otp_debug.py` (NEW)
   - Debug tool for OTP testing
   - Check cache status
   - Clear cache
   - Test complete flow

## Next Steps

1. **Check console output** when sending OTP
2. **Look for cache warnings**
3. **Use debug script** to check cache
4. **Share console output** if issue persists

## Console Output to Share

If issue persists, share this output:

1. **When sending OTP**:
   - The "📤 SEND OTP RESULT" block
   - The "✅ OTP stored" or "❌ WARNING" message

2. **When verifying OTP**:
   - The "🔐 VERIFY OTP" block
   - The "🔐 VERIFICATION RESULT" block

3. **Debug script output**:
   ```bash
   python test_distributor_otp_debug.py check <your_phone>
   ```

This will help identify the exact issue!
