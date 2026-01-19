# Spartan Call Masking - Activated ✅

## New Credentials Configured

**Service**: Telephony Cloud (Spartan)
**Portal**: https://telephonycloud.co.in/portal

### Credentials
- **Service ID**: 2155
- **Username**: 10215500
- **Password**: Admin@007
- **DID Number**: 0120-5018960 (for inbound forwarding)

## Features Implemented

### 1. Test Call Button on User Dashboard
- Added prominent test call section at the top of user dashboard
- Users can test call masking feature with their own number
- Beautiful gradient design with loading states and error handling

### 2. Updated Configuration
- `.env` file updated with new Spartan credentials
- `SPARKTG_DID_NUMBER` set to `01205018960`
- Call masking adapter now uses DID from settings (not hardcoded)

### 3. New Test Endpoint
- **Route**: `POST /gateways/test-call/`
- **Purpose**: Allow logged-in users to test call masking
- **Rate Limit**: 5 calls per hour per user
- **Authentication**: Required

## How It Works

1. User clicks "Test Call Now" button on dashboard
2. System generates a 4-digit PIN
3. PIN is mapped to user's phone number via Spartan API
4. User gets redirected to: `tel:01205018960,<PIN>#`
5. When user dials, call is forwarded to their own number (for testing)

## Testing

### From Dashboard
1. Login to your account
2. Go to Dashboard
3. Click "📞 Test Call Now" button
4. System will generate call link and redirect to dialer
5. Dial the number to test

### API Testing
```bash
curl -X POST https://scan2talk.in/gateways/test-call/ \
  -H "Cookie: sessionid=YOUR_SESSION" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN"
```

## Pricing (Inbound)
- **Channel Charges**: ₹1000/month/Channel
- **Free Minutes**: 1000 mins/month/Channel

## Files Modified

1. `.env` - Updated Spartan credentials
2. `templates/accounts/dashboard.html` - Added test call button
3. `apps/gateways/call_masking_views.py` - Added test_call_masking view
4. `apps/gateways/urls.py` - Added test-call route
5. `apps/communications/adapters/call_masking_adapter.py` - Use DID from settings

## Next Steps

1. Test the call masking feature from dashboard
2. Verify PIN generation and call forwarding
3. Check if inbound forwarding number (0120-5018960) is configured
4. Monitor call logs in Spartan portal

## Notes

- Call masking is now fully integrated with user dashboard
- Users can test the feature without needing a QR code
- All calls are logged and tracked
- PIN expires after 10 minutes for security
