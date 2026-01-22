# Distributor OTP Debug Guide

## Current Status

✅ **Migrations Applied**: All distributor fields are in the database
✅ **Code Implemented**: Distributor registration flow is complete
⚠️ **Issue**: OTP not being received during distributor registration

## Problem Analysis

The distributor registration uses the **same OTP system** as regular QR activation:
- Same `send_otp()` function from `apps/accounts/phone_auth.py`
- Same `SMSCountryOTPService` from `apps/communications/otp_service.py`
- Same credentials from `.env` file

### Why OTP Might Not Be Coming

1. **Development Mode Behavior**
   - When `DEBUG=True`, the OTP service has fallback behavior
   - If SMS API fails, it prints OTP to console instead of failing
   - Check your server console/terminal for OTP output

2. **SMSCountry API Issues**
   - API might return 200 OK but `Success=False` in response body
   - Common reasons: DLT template issues, sender ID problems, invalid credentials
   - The code handles this by printing OTP to console in DEBUG mode

3. **Rate Limiting**
   - 30-second cooldown between OTP requests
   - Check if you're trying to resend too quickly

4. **Lockout Protection**
   - After 3 failed verification attempts, account is locked for 2 hours
   - Check if the phone number is locked out

## Debugging Steps

### Step 1: Run Diagnostic Test

```bash
python test_distributor_otp.py
```

This will:
- Check SMSCountry configuration
- Test OTP sending to a real phone number
- Show detailed API response
- Allow you to test verification

### Step 2: Check Server Logs

When you click "Send OTP" in the distributor registration:

1. **Look for console output** like:
   ```
   ==================================================
   📱 OTP for 9876543210: 123456
   ⚠️  API Error: [error message]
   ==================================================
   ```

2. **Check Django logs** for:
   - `📤 OTP sent and stored for [phone]`
   - `❌ Failed to send OTP for [phone]`
   - SMSCountry API response details

### Step 3: Verify Configuration

Check `.env` file:
```bash
SMSCOUNTRY_AUTH_KEY=qQbyH5R7gFfxivRgYA0d
SMSCOUNTRY_AUTH_TOKEN=NXMG6GLXdUqWqJY7QD6u2oGivqHDHOVK85w3aLT0
```

### Step 4: Test with Known Working Flow

Try the regular QR activation flow:
1. Go to QR activation page
2. Enter phone number
3. Check if OTP comes

If OTP works for QR activation but not distributor registration, there's a code issue.
If OTP doesn't work for either, it's a configuration/API issue.

## Development Mode Workaround

Since `DEBUG=True`, the system will **always show OTP in console** even if SMS fails:

1. Start your Django server in a terminal
2. Go to distributor registration page
3. Enter phone number and click "Send OTP"
4. **Look at the terminal** where Django is running
5. You'll see the OTP printed there
6. Use that OTP to verify

## Common Issues & Solutions

### Issue 1: "OTP not coming" but no error shown

**Solution**: Check the terminal/console where Django server is running. In DEBUG mode, OTP is printed there.

### Issue 2: SMSCountry API returns error

**Possible errors**:
- `DLT template not approved` - Contact SMSCountry support
- `Invalid sender ID` - Verify SENDER_ID in code matches approved sender
- `Invalid credentials` - Check AUTH_KEY and AUTH_TOKEN

**Solution**: The code will print OTP to console in DEBUG mode, so you can still test.

### Issue 3: "Session expired" error

**Solution**: The phone number is stored in session. If you wait too long or refresh, session expires. Start over.

### Issue 4: "Too many failed attempts"

**Solution**: Wait 2 hours or clear cache:
```python
from django.core.cache import cache
cache.delete('otp_lockout_9876543210')  # Replace with actual phone
cache.delete('otp_failed_attempts_9876543210')
```

## Testing in Production

When `DEBUG=False` (production):
- OTP **must** be sent via SMS
- No console fallback
- If SMS fails, user gets error message
- Make sure SMSCountry credentials are valid

## Code Flow

```
User clicks "Become a Distributor"
  ↓
Enter phone number
  ↓
become_distributor view (POST step=1)
  ↓
send_otp(phone) from phone_auth.py
  ↓
SMSCountryOTPService.send_otp()
  ↓
API call to SMSCountry
  ↓
If DEBUG=True and API fails:
  - Print OTP to console
  - Return success=True
  ↓
If DEBUG=False and API fails:
  - Return success=False
  - Show error to user
```

## Next Steps

1. **Run the diagnostic test**: `python test_distributor_otp.py`
2. **Check console output** when sending OTP
3. **Look for printed OTP** in terminal
4. **If OTP is printed**, use it to complete registration
5. **If no OTP printed**, check for error messages in logs

## Files to Check

- `apps/accounts/distributor_views.py` - Distributor registration views
- `apps/accounts/phone_auth.py` - OTP sending wrapper
- `apps/communications/otp_service.py` - SMSCountry OTP service
- `.env` - Configuration
- `gateway_platform/settings.py` - Django settings

## Support

If OTP still doesn't work after following this guide:
1. Share the console output when sending OTP
2. Share any error messages from Django logs
3. Confirm if regular QR activation OTP works
4. Check if SMSCountry account is active and has credits
