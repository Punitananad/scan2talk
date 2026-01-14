# OTP Verification - Quick Start Guide

## 🚀 Setup (5 minutes)

### 1. Add Credentials to `.env`
```bash
# SMSCountry OTP Configuration
SMSCOUNTRY_AUTH_KEY=your_auth_key_here
SMSCOUNTRY_AUTH_TOKEN=your_auth_token_here
```

### 2. Test the System
```bash
python test_otp_system.py
```

### 3. Try Activation Flow
1. Start server: `python manage.py runserver`
2. Go to: `http://localhost:8000/gateways/activate/YOUR_QR_CODE/`
3. Enter phone number (10 digits)
4. Check console for OTP (dev mode)
5. Enter OTP to verify
6. Complete activation

## 📱 How It Works

### User Flow
```
1. Scan QR Code
   ↓
2. Enter Phone Number (10 digits)
   ↓
3. Receive OTP via SMS (6 digits)
   ↓
4. Enter OTP (3 attempts, 5 min expiry)
   ↓
5. Enter Vehicle Details
   ↓
6. Tag Activated ✅
```

### Backend Flow
```
1. Generate 6-digit OTP
   ↓
2. Hash OTP (SHA-256)
   ↓
3. Send via SMSCountry API
   ↓
4. Store hashed OTP in cache (5 min)
   ↓
5. User enters OTP
   ↓
6. Verify hash match
   ↓
7. Invalidate OTP on success
```

## 🔧 Configuration

### SMSCountry API Details
- **Endpoint:** `https://restapi.smscountry.com/v0.1/SMSes/`
- **Auth:** Basic `base64(AuthKey:AuthToken)`
- **Sender ID:** `SCNTLK`
- **DLT Template:** `1707176830112398745`

### Message Template (Fixed)
```
Your OTP for Scan2Talk website registration is {OTP}. Do not share it with anyone. - Scan2Talk
```

### Security Settings
- **OTP Length:** 6 digits
- **Expiry:** 5 minutes
- **Max Attempts:** 3
- **Storage:** Hashed (SHA-256)

## 🧪 Testing

### Development Mode
When credentials not configured:
- OTP printed to console
- No actual SMS sent
- Full flow testable

### Production Mode
With real credentials:
- OTP sent via SMS
- Full DLT compliance
- Production-ready

## 📝 API Request Example

```bash
curl -X POST https://restapi.smscountry.com/v0.1/SMSes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'AuthKey:AuthToken' | base64)" \
  -d '{
    "Text": "Your OTP for Scan2Talk website registration is 123456. Do not share it with anyone. - Scan2Talk",
    "Number": "919876543210",
    "SenderId": "SCNTLK",
    "DLTTemplateId": "1707176830112398745",
    "Tool": "API"
  }'
```

## 🐛 Troubleshooting

### "SMS service not configured"
→ Add credentials to `.env`

### "Invalid phone number"
→ Must be exactly 10 digits

### "OTP expired"
→ Request new OTP (5 min limit)

### "Maximum attempts exceeded"
→ Request new OTP (3 attempts limit)

### "Failed to send OTP"
→ Check credentials and API status

## 📊 Monitoring

### Check Logs
```bash
# Django logs
tail -f logs/django.log

# Look for:
# - "Sending OTP to..."
# - "OTP sent successfully..."
# - "OTP verified successfully..."
```

### Test Endpoints
```bash
# Test OTP generation
python -c "from apps.communications.otp_service import get_otp_service; print(get_otp_service().generate_otp())"

# Test OTP sending
python test_otp_system.py
```

## 🔐 Security Checklist

✅ OTP hashed before storage (SHA-256)
✅ No plain-text OTP in database
✅ 5-minute expiry enforced
✅ 3 attempts limit enforced
✅ OTP invalidated after success
✅ Session-based phone verification
✅ Backend-only SMS sending
✅ DLT compliance maintained

## 🚀 Production Deployment

1. **Get SMSCountry Credentials**
   - Sign up at smscountry.com
   - Get AuthKey and AuthToken
   - Register DLT template

2. **Update Environment**
   ```bash
   SMSCOUNTRY_AUTH_KEY=real_auth_key
   SMSCOUNTRY_AUTH_TOKEN=real_auth_token
   DEBUG=False
   ```

3. **Configure Redis (Recommended)**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

4. **Test Production**
   ```bash
   python test_otp_system.py
   ```

5. **Deploy**
   ```bash
   ./deploy.sh
   ```

## 📚 Files Reference

- `apps/communications/otp_service.py` - OTP service
- `apps/accounts/phone_auth.py` - Phone auth wrapper
- `apps/gateways/qr_views.py` - Activation views
- `templates/gateways/activate_step2_otp.html` - OTP UI
- `test_otp_system.py` - Test suite
- `OTP_VERIFICATION_SYSTEM.md` - Full documentation

## 💡 Tips

- **Dev Mode:** OTP always printed to console
- **Resend:** Users can request new OTP anytime
- **Attempts:** Show remaining attempts in error message
- **Expiry:** Clear expiry time in UI
- **Validation:** Validate phone format before sending

## 🆘 Support

- **SMSCountry:** support@smscountry.com
- **API Docs:** https://www.smscountry.com/docs
- **DLT Portal:** https://www.dltconnect.com

---

**Ready to go!** 🎉

Start with `python test_otp_system.py` to verify everything works.
