# SparkTG Call Masking Integration Guide

## Overview

This system integrates SparkTG/TelephonyCloud Call Masking API to enable privacy-protected phone calls between vehicle owners and people who scan their QR codes.

## How It Works

1. **User scans QR code** on a vehicle
2. **System generates a 4-digit PIN** and maps it to the vehicle owner's phone number via SparkTG API
3. **User receives a click-to-call URL** like `tel:01205019042,4821#`
4. **User clicks/dials** the number
5. **SparkTG connects the call** to the vehicle owner without revealing either party's number

## Configuration

### Environment Variables (.env)

```bash
# SparkTG Call Masking Configuration
SPARKTG_USERNAME=1090600
SPARKTG_PASSWORD=agent007
SPARKTG_DID_NUMBER=01205019042
SPARKTG_SID=906
```

### Settings (gateway_platform/settings.py)

Already configured to read from environment variables:

```python
SPARKTG_USERNAME = env('SPARKTG_USERNAME', default='')
SPARKTG_PASSWORD = env('SPARKTG_PASSWORD', default='')
SPARKTG_DID_NUMBER = env('SPARKTG_DID_NUMBER', default='01205019042')
SPARKTG_SID = env('SPARKTG_SID', default='')
```

## API Usage

### Generate Masked Call URL

**Endpoint:** `POST /gateways/call/<qr_code>/`

**Example:**
```bash
curl -X POST http://localhost:8000/gateways/call/ABC12345/
```

**Response:**
```json
{
  "success": true,
  "pin": "4821",
  "call_url": "tel:01205019042,4821#",
  "did_number": "01205019042",
  "expires_in_minutes": 10
}
```

### Get Call Info (without generating PIN)

**Endpoint:** `GET /gateways/call/<qr_code>/info/`

**Example:**
```bash
curl http://localhost:8000/gateways/call/ABC12345/info/
```

**Response:**
```json
{
  "success": true,
  "did_number": "01205019042",
  "call_masking_enabled": true,
  "gateway_active": true
}
```

## Python Usage

### From Django Views

```python
from apps.communications.call_masking_service import create_masked_call_for_qr
from apps.gateways.qr_models import PreGeneratedQR

# Get QR code
qr = PreGeneratedQR.objects.get(qr_code='ABC12345')

# Generate masked call
result = create_masked_call_for_qr(qr)

if result['success']:
    call_url = result['call_url']
    pin = result['pin']
    # Display to user
else:
    error = result['error']
    # Handle error
```

### Direct Function Call

```python
from apps.communications.call_masking_service import create_masked_call

result = create_masked_call(
    owner_phone_number='9876543210',
    qr_id='ABC12345'
)
```

## Service Layer

### CallMaskingAdapter

Low-level adapter that communicates with SparkTG API:

```python
from apps.communications.adapters.call_masking_adapter import CallMaskingAdapter

adapter = CallMaskingAdapter()
result = adapter.create_masked_call('9876543210', 'QR-001')
```

### Call Masking Service

High-level service functions:

```python
from apps.communications import call_masking_service

# Create masked call for QR
result = call_masking_service.create_masked_call_for_qr(qr_obj)

# Get PIN info
info = call_masking_service.get_pin_info('4821')

# Invalidate PIN
call_masking_service.invalidate_pin('4821')
```

## PIN Management

- **PIN Format:** 4-digit number (1000-9999)
- **Expiry:** 10 minutes
- **Storage:** Redis/Django cache
- **Uniqueness:** Random generation ensures uniqueness

### PIN Cache Structure

```python
cache_key = f"call_mask_pin_{pin}"
cache_value = {
    'owner_phone': '9876543210',
    'qr_id': 'ABC12345',
    'created_at': '2026-01-07T20:00:00Z'
}
```

## Testing

### Test Script

Run the test script:

```bash
python manage.py shell < test_call_masking.py
```

### Manual Testing

1. **Generate a masked call:**
```python
from apps.communications.call_masking_service import create_masked_call
result = create_masked_call('9876543210', 'TEST-001')
print(result)
```

2. **Check the result:**
```python
{
    'success': True,
    'pin': '4821',
    'call_url': 'tel:01205019042,4821#',
    'did_number': '01205019042',
    'expires_in_minutes': 10
}
```

3. **Test the call URL:**
   - On mobile: Click the `call_url`
   - On desktop: Copy and dial manually

## Error Handling

### Common Errors

1. **API Timeout**
```json
{
  "success": false,
  "error": "API request timeout"
}
```

2. **Invalid Credentials**
```json
{
  "success": false,
  "error": "API returned status 401",
  "details": "Unauthorized"
}
```

3. **Missing Owner Phone**
```json
{
  "success": false,
  "error": "Owner phone number not available"
}
```

## Integration Points

### 1. QR Access Page

Add call button to `templates/core/gateway_access.html`:

```html
<button onclick="generateMaskedCall('{{ qr_code }}')">
    📞 Call Owner
</button>

<script>
async function generateMaskedCall(qrCode) {
    const response = await fetch(`/gateways/call/${qrCode}/`, {
        method: 'POST'
    });
    const data = await response.json();
    
    if (data.success) {
        window.location.href = data.call_url;
    } else {
        alert('Error: ' + data.error);
    }
}
</script>
```

### 2. Gateway Access View

Modify `apps/core/views.py` to include call masking option:

```python
def get(self, request, identifier):
    # ... existing code ...
    
    context = {
        'gateway': gateway,
        'call_masking_enabled': settings.SPARKTG_USERNAME and settings.SPARKTG_PASSWORD,
        # ... other context ...
    }
    
    return render(request, 'core/gateway_access.html', context)
```

## Security Considerations

1. **Rate Limiting:** 10 calls per hour per IP (configured in views)
2. **PIN Expiry:** 10 minutes automatic expiry
3. **No Phone Disclosure:** Neither party sees the other's number
4. **Audit Trail:** All calls logged via Django logging

## Monitoring

### Logs

Check logs for call masking activity:

```bash
# Success
INFO: Call mask created: PIN=4821, QR=ABC12345, Phone=****3210

# Failure
ERROR: SparkTG API error: API returned status 500
```

### Cache Monitoring

Check active PINs:

```python
from django.core.cache import cache
info = cache.get('call_mask_pin_4821')
print(info)
```

## Production Checklist

- [ ] Set correct SparkTG credentials in production .env
- [ ] Enable HTTPS for secure API calls
- [ ] Configure Redis for production cache
- [ ] Set up monitoring/alerting for API failures
- [ ] Test with real phone numbers
- [ ] Verify rate limiting is working
- [ ] Check logs are being captured
- [ ] Test PIN expiry behavior

## Support

For SparkTG API issues:
- Portal: https://telephonycloud.co.in/portal/
- Login: 1090600 / agent007
- Contact: Navodit Gupta <navodit@sparktg.com>

## Files Created

1. `apps/communications/adapters/call_masking_adapter.py` - API adapter
2. `apps/communications/call_masking_service.py` - Service layer
3. `apps/gateways/call_masking_views.py` - Django views
4. `test_call_masking.py` - Test script
5. `CALL_MASKING_GUIDE.md` - This documentation

## Next Steps

1. Test the integration with real credentials
2. Add call button to QR access pages
3. Update UI templates
4. Monitor API usage and costs
5. Implement call analytics/reporting
