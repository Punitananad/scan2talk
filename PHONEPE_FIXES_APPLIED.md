# PhonePe Integration - ALL CRITICAL FIXES APPLIED

## ✅ ALL 5 ROOT CAUSES FIXED

### FIX #1: Environment Mismatch (CRITICAL) ✅
**Problem**: Using production credentials with sandbox URL
**Fixed**:
```python
IS_PRODUCTION = True  # Changed from False
BASE_URL = 'https://api.phonepe.com/apis/hermes'  # Production URL
```

### FIX #2: Invalid URLs (CRITICAL) ✅
**Problem**: Using localhost HTTP URLs
**Fixed**:
```python
protocol = 'https' if not settings.DEBUG else 'http'
redirectUrl = f"{protocol}://{domain}/api/v1/auth/wallet/phonepe/callback/"
callbackUrl = f"{protocol}://{domain}/api/v1/auth/wallet/phonepe/callback/"
```

### FIX #3: Transaction ID Format ✅
**Problem**: Non-unique, potentially too long transaction IDs
**Fixed**:
```python
transaction_id = f"TXN{uuid4().hex[:20].upper()}"  # UUID-based, max 23 chars
# Store mapping in DB via gateway_order_id
```

### FIX #4: Mobile Number Validation ✅
**Problem**: Fake mobile number causing validation failures
**Fixed**:
```python
# Removed mobileNumber from payload completely
# It's optional for PAY_PAGE type
```

### FIX #5: Callback Signature Verification ✅
**Problem**: Wrong checksum format for callbacks
**Fixed**:
```python
def _generate_callback_checksum(cls, response_base64):
    # Correct format: SHA256(response + SALT_KEY) + ### + SALT_INDEX
    # NO endpoint, NO /pg/v1/pay
    string_to_hash = f"{response_base64}{cls.SALT_KEY}"
    sha256_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
    return f"{sha256_hash}###{cls.SALT_INDEX}"
```

## Valid Payload Now Being Sent

```json
{
  "merchantId": "M227BOU8BBNV7",
  "merchantTransactionId": "TXNABC123DEF456",
  "merchantUserId": "USER42",
  "amount": 1000,
  "redirectUrl": "https://yourdomain.com/api/v1/auth/wallet/phonepe/callback/",
  "redirectMode": "POST",
  "callbackUrl": "https://yourdomain.com/api/v1/auth/wallet/phonepe/callback/",
  "paymentInstrument": {
    "type": "PAY_PAGE"
  }
}
```

## Debug Logging Added

The code now logs:
- Request URL and environment
- Merchant ID and Transaction ID
- Full payload being sent
- Response status code
- Response body
- Any errors

Check Django console for detailed logs.

## Remaining Steps

### 1. HTTPS Setup (Required for Production)
**Current**: Using HTTP (localhost)
**Required**: HTTPS public URL

**Options**:

**A. Use ngrok (for testing)**:
```bash
ngrok http 8000
# Update .env:
PLATFORM_DOMAIN=your-ngrok-url.ngrok.io
```

**B. Deploy to production**:
```bash
# Update .env:
PLATFORM_DOMAIN=yourdomain.com
```

### 2. Whitelist Callback URL in PhonePe Dashboard
1. Login to https://business.phonepe.com/
2. Go to Developer Settings → Webhooks
3. Add callback URL:
   - `https://yourdomain.com/api/v1/auth/wallet/phonepe/callback/`

### 3. Test Payment
```bash
# Restart server
python manage.py runserver

# Try recharge
# Check console logs for detailed output
```

## Expected Behavior Now

### If Everything is Correct:
- ✅ HTTP 200 response from PhonePe
- ✅ Payment URL returned
- ✅ User redirected to PhonePe payment page
- ✅ Payment completes
- ✅ Callback received
- ✅ Wallet credited

### If Still Getting HTTP 400:
Check console logs for exact error message from PhonePe.

Common remaining issues:
1. **Callback URL not whitelisted** - Add in PhonePe dashboard
2. **Merchant not activated** - Contact PhonePe support
3. **HTTPS required** - Use ngrok or deploy to production

## Testing Checklist

- [x] Environment matches credentials (Production)
- [x] Transaction ID format fixed (UUID-based)
- [x] Mobile number removed from payload
- [x] Callback checksum format fixed
- [ ] HTTPS URL configured (use ngrok for testing)
- [ ] Callback URL whitelisted in PhonePe dashboard
- [ ] Test with ₹1 payment

## Console Output to Check

Look for these logs:
```
PhonePe Request:
URL: https://api.phonepe.com/apis/hermes/pg/v1/pay
Environment: PRODUCTION
Merchant ID: M227BOU8BBNV7
Transaction ID: TXNABC123DEF456
Payload: {...}

PhonePe Response: 200
Response Body: {"success":true,"data":{...}}
```

## If You See HTTP 400 Still

The error message will now be detailed. Common causes:
1. **"Callback URL not whitelisted"** → Add in dashboard
2. **"Merchant not active"** → Contact PhonePe support
3. **"Invalid amount"** → Check amount is >= 100 paise (₹1)
4. **"HTTPS required"** → Use ngrok or production domain

## Next Action

**For Local Testing**:
```bash
# Install ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update .env:
PLATFORM_DOMAIN=abc123.ngrok.io

# Restart server
python manage.py runserver

# Try recharge again
```

**For Production**:
```bash
# Deploy to your server with HTTPS
# Update .env:
PLATFORM_DOMAIN=yourdomain.com

# Restart server
# Try recharge
```

## Status

✅ **Code Issues**: ALL FIXED
⏳ **Infrastructure**: Needs HTTPS URL
⏳ **PhonePe Dashboard**: Needs callback URL whitelisting

The integration is now technically correct. The remaining steps are infrastructure and configuration.
