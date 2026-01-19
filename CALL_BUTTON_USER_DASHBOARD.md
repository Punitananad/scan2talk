# Call Button Integration - User Dashboard 📞

## What's New

A beautiful, prominent **Test Call Masking** feature has been added to the user dashboard!

## Visual Design

```
┌─────────────────────────────────────────────────────────────┐
│  📞 Test Call Masking                                       │
│  Try our secure call feature - your number stays private!  │
│                                                             │
│  [📞 Test Call Now]                                        │
│                                                             │
│  ✅ Call link generated!                                   │
│  Redirecting to dialer...                                  │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Prominent Placement
- Located at the top of the dashboard
- Eye-catching gradient background (green to blue)
- Large phone icon for visual appeal

### 2. Interactive States
- **Default**: Green "Test Call Now" button
- **Loading**: Spinner with "Generating secure call link..."
- **Success**: Green checkmark with "Call link generated!"
- **Error**: Red alert with error message

### 3. User Experience
1. User clicks button
2. System generates PIN via Spartan API
3. Success message appears
4. Auto-redirects to phone dialer after 1 second
5. User dials and call connects to their own number

## Technical Implementation

### Frontend (dashboard.html)
```javascript
async function testCallMasking() {
    // Show loading state
    // Call API: POST /gateways/test-call/
    // Handle success/error
    // Redirect to tel: URL
}
```

### Backend (call_masking_views.py)
```python
@csrf_exempt
@require_http_methods(["POST"])
@ratelimit(key='user', rate='5/h', method='POST')
def test_call_masking(request):
    # Get user's phone number
    # Generate PIN via CallMaskingAdapter
    # Return call URL: tel:01205018960,<PIN>#
```

### API Endpoint
- **URL**: `/gateways/test-call/`
- **Method**: POST
- **Auth**: Required (logged-in users only)
- **Rate Limit**: 5 calls per hour per user

### Response Format
```json
{
    "success": true,
    "pin": "1234",
    "call_url": "tel:01205018960,1234#",
    "did_number": "01205018960",
    "expires_in_minutes": 10
}
```

## Security Features

1. **Authentication Required**: Only logged-in users can test
2. **Rate Limiting**: 5 calls per hour to prevent abuse
3. **PIN Expiry**: PINs expire after 10 minutes
4. **CSRF Protection**: CSRF token required for API calls

## User Flow

```
Dashboard → Click "Test Call Now" 
    ↓
Generate PIN (1234)
    ↓
Map PIN to User's Phone
    ↓
Return: tel:01205018960,1234#
    ↓
Redirect to Phone Dialer
    ↓
User Dials → Call Connects
```

## Benefits

1. **Easy Testing**: Users can test call masking without QR codes
2. **Privacy Demo**: Shows how their number stays private
3. **Confidence Building**: Users see the feature works before using it
4. **Onboarding**: Great way to introduce the call masking feature

## Mobile Responsive

- Full width on mobile devices
- Touch-friendly button size
- Optimized for small screens
- Icon hidden on very small screens

## Error Handling

- No phone number → "Please update your profile"
- API failure → "Internal server error"
- Rate limit exceeded → "Too many requests"
- Network error → "Failed to generate call link"

## Next Steps

1. Test the button on dashboard
2. Verify call connects properly
3. Check PIN expiry (10 minutes)
4. Monitor rate limiting
5. Add analytics tracking

## Files Modified

1. `templates/accounts/dashboard.html` - Added call button UI
2. `apps/gateways/call_masking_views.py` - Added test endpoint
3. `apps/gateways/urls.py` - Added route
4. `.env` - Updated Spartan credentials
5. `.env.example` - Updated example credentials

## Spartan Configuration

- **Service ID**: 2155
- **Username**: 10215500
- **Password**: Admin@007
- **DID Number**: 01205018960
- **Portal**: https://telephonycloud.co.in/portal
