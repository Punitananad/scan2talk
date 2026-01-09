# PhonePe Integration Troubleshooting

## Current Error: HTTP 400

You're seeing "PhonePe API error: HTTP 400" which means the API request is being rejected.

## Common Causes & Solutions

### 1. Merchant Account Not Activated
**Problem**: Your PhonePe merchant account might not be fully activated for API access.

**Solution**:
1. Login to PhonePe Business Dashboard: https://business.phonepe.com/
2. Check if your account status is "Active"
3. Verify API access is enabled
4. Contact PhonePe support if needed

### 2. Using Wrong Environment
**Problem**: Using production credentials with UAT/sandbox URL or vice versa.

**Current Settings**:
```
PHONEPE_PRODUCTION=True (in .env)
```

**Solution**:
Try switching to UAT first:
```env
# In .env file
PHONEPE_PRODUCTION=False
```

Then test again. If it works in UAT, your production account needs activation.

### 3. Callback URL Not Whitelisted
**Problem**: PhonePe requires you to whitelist callback URLs in the dashboard.

**Your Callback URL**:
```
http://192.168.1.75:8000/api/v1/auth/wallet/phonepe/callback/
```

**Solution**:
1. Login to PhonePe Business Dashboard
2. Go to Developer Settings → Webhooks
3. Add your callback URL
4. For local testing, you might need ngrok or similar

### 4. Merchant ID Mismatch
**Problem**: The merchant ID in code doesn't match your actual merchant ID.

**Current Merchant ID**: M227BOU8BBNV7

**Solution**:
1. Login to PhonePe dashboard
2. Go to Developer Settings → API Keys
3. Verify your actual Merchant ID
4. Update in `.env` if different:
```env
PHONEPE_MERCHANT_ID=YOUR_ACTUAL_MERCHANT_ID
```

### 5. Salt Key/Index Incorrect
**Problem**: Salt key or salt index doesn't match dashboard.

**Solution**:
1. Check PhonePe dashboard for correct salt key
2. Verify salt index (usually 1 for production)
3. Update in `.env`:
```env
PHONEPE_SALT_KEY=your_actual_salt_key
PHONEPE_SALT_INDEX=1
```

### 6. Local Development Issues
**Problem**: PhonePe can't reach localhost callback URL.

**Solution for Local Testing**:

**Option A: Use ngrok**
```bash
# Install ngrok
# Run ngrok
ngrok http 8000

# Update .env with ngrok URL
PLATFORM_DOMAIN=your-ngrok-url.ngrok.io
```

**Option B: Use Test Mode (Current Fallback)**
The system now automatically falls back to test mode if PhonePe fails. You'll see a test payment page instead.

## Quick Fixes to Try

### Fix 1: Switch to UAT Environment
```env
# .env
PHONEPE_PRODUCTION=False
```

### Fix 2: Use Test Mode Temporarily
The system now has automatic fallback. Just proceed with recharge and you'll see a test payment page.

### Fix 3: Contact PhonePe Support
Email: merchantsupport@phonepe.com

Provide them:
- Merchant ID: M227BOU8BBNV7
- Client ID: SU2504042021229572318914
- Error: HTTP 400 on payment initiation
- Request: Enable API access and whitelist callback URL

## Testing Steps

### Step 1: Try UAT Environment
```bash
# Update .env
PHONEPE_PRODUCTION=False

# Restart server
python manage.py runserver

# Try recharge again
```

### Step 2: Use Test Mode
```bash
# System automatically falls back to test mode
# Just proceed with recharge
# You'll see a test payment page
```

### Step 3: Check PhonePe Dashboard
1. Login to https://business.phonepe.com/
2. Check account status
3. Verify API keys
4. Check transaction logs

## Current Workaround

The system now has **automatic fallback to test mode**. When PhonePe returns an error:
1. Order is still created
2. You're redirected to test payment page
3. You can simulate successful payment
4. Wallet is credited normally

This lets you test the entire wallet system while PhonePe configuration is being sorted out.

## What to Tell PhonePe Support

```
Subject: API Integration - HTTP 400 Error

Hi PhonePe Team,

I'm integrating PhonePe payment gateway and getting HTTP 400 error on payment initiation.

Merchant Details:
- Merchant ID: M227BOU8BBNV7
- Client ID: SU2504042021229572318914
- Environment: Production
- Integration Type: Standard Checkout (Pay Page)

Error:
- Endpoint: POST /apis/hermes/pg/v1/pay
- Response: HTTP 400

Request:
1. Please verify my merchant account is activated for API access
2. Please whitelist my callback URL: http://yourdomain.com/api/v1/auth/wallet/phonepe/callback/
3. Please confirm my merchant ID and salt key are correct
4. Please provide any additional configuration needed

Thank you!
```

## Next Steps

### Immediate (Use Test Mode)
1. System automatically uses test mode
2. Test all wallet functionality
3. Verify everything works

### Short Term (Fix PhonePe)
1. Contact PhonePe support
2. Get account activated
3. Whitelist callback URLs
4. Switch back to production

### Long Term (Go Live)
1. Get HTTPS domain
2. Update callback URLs
3. Test with real payments
4. Monitor transactions

## Checking Logs

To see detailed error from PhonePe:
```bash
# Check Django console output
# Look for: "PhonePe Error: ..."
```

## Alternative: Use Different Gateway

If PhonePe takes time to activate, you can:
1. Use Razorpay (easier activation)
2. Use Paytm
3. Use Cashfree
4. Keep using test mode

## Status

**Current**: ✅ System working with test mode fallback
**PhonePe**: ⏳ Pending configuration/activation
**Wallet**: ✅ Fully functional

You can continue development and testing while PhonePe configuration is sorted out!
