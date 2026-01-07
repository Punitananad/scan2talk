# Testing Call Masking API with cURL

## Prerequisites
You need an activated QR code. Let's check what QR codes exist:

### Step 1: Check Available QR Codes
```bash
# Login to admin panel
# Go to: http://localhost:8000/admin/
# Username: admin@example.com
# Password: admin123

# Or check in Django shell:
python manage.py shell
>>> from apps.gateways.qr_models import PreGeneratedQR
>>> qrs = PreGeneratedQR.objects.filter(status='activated')
>>> for qr in qrs:
...     print(f"QR Code: {qr.qr_code}, Owner: {qr.owner}")
```

### Step 2: Test with cURL

**Test 1: Generate Masked Call**
```bash
curl -X POST http://localhost:8000/gateways/call/YOUR_QR_CODE/
```

Example with a real QR code:
```bash
curl -X POST http://localhost:8000/gateways/call/ABC12345/
```

**Expected Response:**
```json
{
  "success": true,
  "pin": "4821",
  "call_url": "tel:01205019042,4821#",
  "did_number": "01205019042",
  "expires_in_minutes": 10
}
```

**Test 2: Get Call Info (No PIN Generation)**
```bash
curl http://localhost:8000/gateways/call/ABC12345/info/
```

**Expected Response:**
```json
{
  "success": true,
  "did_number": "01205019042",
  "call_masking_enabled": true,
  "gateway_active": true
}
```

### Step 3: Test Error Cases

**Test with Invalid QR Code:**
```bash
curl -X POST http://localhost:8000/gateways/call/INVALID123/
```

**Expected Response:**
```json
{
  "success": false,
  "error": "QR code not found or not activated"
}
```

## Using PowerShell (Windows)

```powershell
# Test 1: Generate masked call
Invoke-RestMethod -Uri "http://localhost:8000/gateways/call/ABC12345/" -Method POST

# Test 2: Get call info
Invoke-RestMethod -Uri "http://localhost:8000/gateways/call/ABC12345/info/" -Method GET
```

## Using Python requests

```python
import requests

# Test 1: Generate masked call
response = requests.post('http://localhost:8000/gateways/call/ABC12345/')
print(response.json())

# Test 2: Get call info
response = requests.get('http://localhost:8000/gateways/call/ABC12345/info/')
print(response.json())
```
