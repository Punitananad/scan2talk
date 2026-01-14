# OTP Verification System - SMSCountry Integration

## Overview
Complete OTP verification system integrated with SMSCountry REST API for tag activation. Enforces mobile number verification before users can activate their QR tags.

## Features
✅ **SMSCountry REST API Integration** (AuthKey-based, NO SID)
✅ **India DLT Compliance** - Fixed template and sender ID
✅ **Secure OTP Storage** - SHA-256 hashed in cache
✅ **5-minute OTP Expiry**
✅ **3 Verification Attempts Limit**
✅ **OTP Resend Functionality**
✅ **Backend-only Execution** - No frontend SMS calls
✅ **Production-ready Error Handling**

## Configuration

### 1. Environment Variables
Add to `.env` file:

```bash
# SMSCountry OTP Configuration (AuthKey-based, NO SID)
SMSCOUNTRY_AUTH_KEY=your_auth_key_here
SMSCOUNTRY_AUTH_TOKEN=your_auth_token_here
```

### 2. SMSCountry API Specifications

**API Endpoint:**
```
https://restapi.smscountry.com/v0.1/SMSes/
```

**Authentication:**
- Method: Basic Authentication
- Format: `Basic base64(AuthKey:AuthToken)`
- NO Account SID required

**Fixed Configuration:**
- Sender ID: `SCNTLK`
- DLT Template ID: `1707176830112398745`
- Tool: `API`

**Message Template (DLT-approved, DO NOT MODIFY):**
```
Your OTP for Scan2Talk website registration is {OTP}. Do not share it with anyone. - Scan2Talk
```

## Implementation Details

### Files Created/Modified

1. **`apps/communications/otp_service.py`** (NEW)
   - SMSCountry OTP service class
   - OTP generation (6-digit secure random)
   - OTP hashing (SHA-256)
   - SMS sending via REST API
   - OTP verification with attempt limiting
   - Resend functionality

2. **`apps/accounts/phone_auth.py`** (UPDATED)
   - Integrated with OTP service
   - Wrapper functions for send/verify/resend

3. **`apps/gateways/qr_views.py`** (UPDATED)
   - Enforced OTP verification in activation flow
   - Added resend OTP endpoint
   - 3-step activation process

4. **`templates/gateways/activate_step2_otp.html`** (UPDATED)
   - 6-digit OTP input
   - Resend button
   - Security notices

5. **`gateway_platform/settings.py`** (UPDATED)
   - Added SMSCountry configuration

6. **`.env` and `.env.example`** (UPDATED)
   - Added SMSCountry credentials

## Activation Flow

### Step 1: Enter Phone Number
- User enters 10-digit mobile number
- System validates format
- Generates 6-digit OTP
- Sends via SMSCountry API
- Stores hashed OTP in cache (5 min expiry)

### Step 2: Verify OTP
- User enters 6-digit OTP
- System verifies against hashed value
- 3 attempts allowed
- Option to resend OTP
- On success, marks phone as verified

### Step 3: Enter Vehicle Details
- Only accessible after OTP verification
- User enters name, vehicle number, etc.
- Creates user account and activates tag

## Security Features

### OTP Storage
- **Hashing:** SHA-256 before storage
- **Storage:** Django cache (in-memory/Redis)
- **Expiry:** 5 minutes
- **Invalidation:** After success or max attempts

### Attempt Limiting
- Maximum 3 verification attempts
- Counter decremented on each failed attempt
- OTP deleted after max attempts exceeded

### Session Management
- Phone number stored in session
- Verification status tracked
- 10-minute session timeout

## API Request Format

### Send SMS Request
```json
POST https://restapi.smscountry.com/v0.1/SMSes/
Headers:
  Content-Type: application/json
  Authorization: Basic <base64(AuthKey:AuthToken)>

Body:
{
  "Text": "Your OTP for Scan2Talk website registration is 123456. Do not share it with anyone. - Scan2Talk",
  "Number": "919876543210",
  "SenderId": "SCNTLK",
  "DLTTemplateId": "1707176830112398745",
  "Tool": "API"
}
```

### Success Response
```json
{
  "Success": true,
  "Message": "Message sent successfully",
  "MessageId": "..."
}
```

## Development Mode

When `DEBUG=True` and credentials not configured:
- OTP is generated but not sent
- Logged to console for testing
- Returns success to allow development

## Testing

### Manual Testing
1. Start server: `python manage.py runserver`
2. Navigate to QR activation page
3. Enter phone number
4. Check console for OTP (dev mode) or SMS (production)
5. Enter OTP to verify
6. Complete activation

### Test Script
```bash
python test_otp_system.py
```

## Production Deployment

### Prerequisites
1. SMSCountry account with AuthKey and AuthToken
2. DLT registration completed
3. Sender ID approved: `SCNTLK`
4. Template approved: ID `1707176830112398745`

### Deployment Steps
1. Update `.env` with real credentials:
   ```bash
   SMSCOUNTRY_AUTH_KEY=your_real_auth_key
   SMSCOUNTRY_AUTH_TOKEN=your_real_auth_token
   ```

2. Set production mode:
   ```bash
   DEBUG=False
   ```

3. Configure Redis for cache (recommended):
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

4. Test OTP sending:
   ```bash
   python test_otp_system.py --production
   ```

5. Deploy and monitor logs

## Error Handling

### Common Errors

**"SMS service not configured"**
- Credentials missing in `.env`
- Check `SMSCOUNTRY_AUTH_KEY` and `SMSCOUNTRY_AUTH_TOKEN`

**"Invalid phone number format"**
- Must be exactly 10 digits
- No country code needed (added automatically)

**"OTP expired or not found"**
- OTP expired after 5 minutes
- User should request new OTP

**"Maximum verification attempts exceeded"**
- User entered wrong OTP 3 times
- Must request new OTP

**"Failed to send OTP"**
- Network error or API timeout
- Check SMSCountry API status
- Verify credentials

## Monitoring

### Logs to Monitor
```python
logger.info(f"Sending OTP to {phone_number} via SMSCountry")
logger.info(f"SMSCountry Response: {response.status_code} - {response.text}")
logger.info(f"OTP sent successfully to {phone_number}")
logger.info(f"OTP verified successfully for {phone_number}")
logger.error(f"SMSCountry API error: {response.status_code} - {response.text}")
```

### Metrics to Track
- OTP send success rate
- OTP verification success rate
- Average verification time
- Failed attempt rate
- API response times

## Compliance

### India DLT Rules
✅ Registered sender ID: `SCNTLK`
✅ Approved template ID: `1707176830112398745`
✅ Fixed message template (no modifications)
✅ No promotional content
✅ Clear opt-out information

### Data Protection
✅ OTP hashed before storage
✅ No plain-text OTP storage
✅ Automatic expiry (5 minutes)
✅ Secure session management
✅ No OTP in logs (production)

## Support

### SMSCountry Support
- Website: https://www.smscountry.com
- API Docs: https://www.smscountry.com/docs
- Support: support@smscountry.com

### Troubleshooting
1. Check credentials in `.env`
2. Verify DLT template approval
3. Check API endpoint accessibility
4. Review Django logs
5. Test with curl/Postman

## Future Enhancements
- [ ] Rate limiting per phone number
- [ ] SMS delivery status tracking
- [ ] Multi-language OTP messages
- [ ] Fallback to voice OTP
- [ ] Analytics dashboard
- [ ] A/B testing for OTP length

---

**Last Updated:** January 14, 2026
**Version:** 1.0.0
**Status:** Production Ready
