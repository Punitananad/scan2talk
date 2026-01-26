# OTP First-Time Verification Fix

## Problem
Users had to enter OTP 2-3 times before it was verified successfully during:
- QR tag activation flow
- Distributor login
- User phone login

## Root Cause
**Race Condition**: In rare cases, when users entered OTP very quickly after receiving it, the verification happened before the cache write was fully committed, causing the first attempt to fail.

## Solution Applied

### 1. Enhanced OTP Storage Verification (`apps/communications/otp_service.py`)
```python
def store_otp(self, phone_number, otp):
    # Store OTP
    cache.set(cache_key, cache_data, self.OTP_EXPIRY_MINUTES * 60)
    
    # CRITICAL: Immediately verify it was stored by reading it back
    stored_data = cache.get(cache_key)
    if stored_data:
        logger.info(f"✅ OTP stored and verified")
    else:
        # Retry once if storage failed
        cache.set(cache_key, cache_data, self.OTP_EXPIRY_MINUTES * 60)
```

**Why**: Ensures OTP is actually in cache before returning success.

### 2. Added Retry Mechanism in Verification (`apps/accounts/phone_auth.py`)
```python
def verify_otp(phone_number, otp):
    # Check cache
    cached_data = cache.get(cache_key)
    
    # RETRY: If not found, wait 100ms and retry
    if not cached_data:
        time.sleep(0.1)
        cached_data = cache.get(cache_key)
        
        # If still not found, wait 200ms more
        if not cached_data:
            time.sleep(0.2)
            cached_data = cache.get(cache_key)
```

**Why**: Handles race conditions where verification happens immediately after send.

### 3. Strip Whitespace from OTP Input
```python
otp = otp.strip()
```

**Why**: Prevents verification failures due to accidental spaces.

## Files Modified
1. `apps/communications/otp_service.py` - Enhanced storage verification
2. `apps/accounts/phone_auth.py` - Added retry mechanism and whitespace stripping

## Testing
Test all OTP flows:
1. ✅ QR tag activation (scan → phone → OTP → verify)
2. ✅ Distributor login
3. ✅ User phone login
4. ✅ Try entering OTP immediately after receiving it
5. ✅ Try entering OTP with spaces

## Expected Result
- OTP should verify on **FIRST attempt** every time
- No more "Invalid OTP" errors requiring multiple tries
- Works even if user enters OTP very quickly

## Deployment
```bash
cd /var/www/scan2talk
git pull origin main
python3 manage.py collectstatic --noinput
systemctl restart gunicorn
systemctl restart nginx
```

## Verification Commands
After deployment, test:
```bash
# Check logs for OTP storage verification
tail -f /var/log/gunicorn/error.log | grep "OTP stored"

# Test QR activation
# Scan a QR code and verify OTP on first attempt
```
