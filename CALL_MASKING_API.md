# Call Masking API Documentation

## Endpoints

### 1. Generate Masked Call URL

Creates a temporary PIN mapping and returns a click-to-call URL.

**Endpoint:** `POST /gateways/call/<qr_code>/`

**Method:** POST

**Authentication:** None (public endpoint, rate-limited)

**Rate Limit:** 10 requests per hour per IP

**Parameters:**
- `qr_code` (path parameter): The QR code identifier

**Request Example:**
```bash
curl -X POST http://localhost:8000/gateways/call/ABC12345/
```

**Success Response (200):**
```json
{
  "success": true,
  "pin": "4821",
  "call_url": "tel:01205019042,4821#",
  "did_number": "01205019042",
  "expires_in_minutes": 10
}
```

**Error Responses:**

**400 - Gateway Not Active:**
```json
{
  "success": false,
  "error": "Gateway is not active"
}
```

**404 - QR Code Not Found:**
```json
{
  "success": false,
  "error": "QR code not found or not activated"
}
```

**500 - API Error:**
```json
{
  "success": false,
  "error": "API request timeout"
}
```

---

### 2. Get Call Information

Retrieves call masking configuration without generating a PIN.

**Endpoint:** `GET /gateways/call/<qr_code>/info/`

**Method:** GET

**Authentication:** None

**Parameters:**
- `qr_code` (path parameter): The QR code identifier

**Request Example:**
```bash
curl http://localhost:8000/gateways/call/ABC12345/info/
```

**Success Response (200):**
```json
{
  "success": true,
  "did_number": "01205019042",
  "call_masking_enabled": true,
  "gateway_active": true
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "QR code not found or not activated"
}
```

---

## Response Fields

### Generate Masked Call Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |
| `pin` | string | 4-digit PIN for the call (1000-9999) |
| `call_url` | string | Click-to-call URL with embedded PIN |
| `did_number` | string | DID number to dial |
| `expires_in_minutes` | integer | PIN validity duration (10 minutes) |
| `error` | string | Error message (only if success=false) |

### Get Call Info Response

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |
| `did_number` | string | DID number for calls |
| `call_masking_enabled` | boolean | Whether call masking is configured |
| `gateway_active` | boolean | Whether the gateway is active |
| `error` | string | Error message (only if success=false) |

---

## Usage Flow

### Standard Flow

1. **User scans QR code** → Lands on gateway access page
2. **User clicks "Call Owner"** → Frontend calls `POST /gateways/call/<qr_code>/`
3. **Backend generates PIN** → Calls SparkTG API to map PIN to owner's phone
4. **Backend returns call URL** → `tel:01205019042,4821#`
5. **User's phone dials** → Automatically includes PIN
6. **SparkTG connects call** → Routes to owner without revealing numbers

### Alternative Flow (Manual Dial)

1. User calls `GET /gateways/call/<qr_code>/info/` to get DID number
2. User manually dials the DID number
3. IVR prompts for PIN
4. User enters PIN from previous `POST` call
5. Call connects to owner

---

## JavaScript Integration

### Basic Example

```javascript
async function callOwner(qrCode) {
    try {
        const response = await fetch(`/gateways/call/${qrCode}/`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to call URL (works on mobile)
            window.location.href = data.call_url;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    }
}
```

### With Loading State

```javascript
async function callOwner(qrCode) {
    const button = document.getElementById('callBtn');
    button.disabled = true;
    button.textContent = 'Connecting...';
    
    try {
        const response = await fetch(`/gateways/call/${qrCode}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = data.call_url;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        button.disabled = false;
        button.textContent = 'Call Owner';
    }
}
```

---

## Python Integration

### From Django View

```python
from apps.communications.call_masking_service import create_masked_call_for_qr
from apps.gateways.qr_models import PreGeneratedQR

def my_view(request, qr_code):
    qr = PreGeneratedQR.objects.get(qr_code=qr_code)
    result = create_masked_call_for_qr(qr)
    
    if result['success']:
        return JsonResponse(result)
    else:
        return JsonResponse(result, status=500)
```

### Direct Service Call

```python
from apps.communications.call_masking_service import create_masked_call

result = create_masked_call(
    owner_phone_number='9876543210',
    qr_id='ABC12345'
)

if result['success']:
    call_url = result['call_url']
    pin = result['pin']
```

---

## Error Handling

### Client-Side

```javascript
try {
    const response = await fetch(`/gateways/call/${qrCode}/`, {
        method: 'POST'
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error);
    }
    
    // Success
    window.location.href = data.call_url;
    
} catch (error) {
    console.error('Call masking error:', error);
    showError(error.message);
}
```

### Server-Side

```python
from apps.communications.call_masking_service import create_masked_call_for_qr

try:
    result = create_masked_call_for_qr(qr)
    
    if not result['success']:
        logger.error(f"Call masking failed: {result['error']}")
        return JsonResponse(result, status=500)
    
    return JsonResponse(result)
    
except Exception as e:
    logger.exception("Unexpected error in call masking")
    return JsonResponse({
        'success': False,
        'error': 'Internal server error'
    }, status=500)
```

---

## Testing

### cURL Examples

**Generate masked call:**
```bash
curl -X POST http://localhost:8000/gateways/call/ABC12345/ \
  -H "Content-Type: application/json"
```

**Get call info:**
```bash
curl http://localhost:8000/gateways/call/ABC12345/info/
```

### Python Test

```python
import requests

# Generate masked call
response = requests.post('http://localhost:8000/gateways/call/ABC12345/')
data = response.json()

if data['success']:
    print(f"Call URL: {data['call_url']}")
    print(f"PIN: {data['pin']}")
else:
    print(f"Error: {data['error']}")
```

---

## Rate Limiting

- **Endpoint:** `POST /gateways/call/<qr_code>/`
- **Limit:** 10 requests per hour per IP address
- **Response when exceeded:** HTTP 429 Too Many Requests

---

## Security

1. **No Authentication Required:** Public endpoint for ease of use
2. **Rate Limited:** Prevents abuse
3. **PIN Expiry:** 10 minutes automatic expiry
4. **No Phone Disclosure:** Neither party sees the other's number
5. **Audit Logging:** All requests logged

---

## Support

For API issues or questions:
- Check logs: `tail -f logs/django.log`
- Review documentation: `CALL_MASKING_GUIDE.md`
- Contact: SparkTG support
