# Testing Call Masking API with Postman or Browser

## Using Postman

### Test 1: Generate Masked Call

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/gateways/call/ABC12345/`
- Headers: None required
- Body: None required

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

### Test 2: Get Call Info

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/gateways/call/ABC12345/info/`

**Expected Response:**
```json
{
  "success": true,
  "did_number": "01205019042",
  "call_masking_enabled": true,
  "gateway_active": true
}
```

## Using Browser

### Test Get Call Info (GET request)
Simply open in browser:
```
http://localhost:8000/gateways/call/ABC12345/info/
```

You should see JSON response.

### Test Generate Masked Call (POST request)
You need a tool for POST requests. Use browser console:

```javascript
// Open browser console (F12) and paste:
fetch('http://localhost:8000/gateways/call/ABC12345/', {
    method: 'POST'
})
.then(r => r.json())
.then(data => console.log(data));
```

## Using Thunder Client (VS Code Extension)

1. Install Thunder Client extension in VS Code
2. Create new request
3. Set method to POST
4. Set URL to `http://localhost:8000/gateways/call/ABC12345/`
5. Click Send

## Import Postman Collection

Save this as `call_masking_api.postman_collection.json`:

```json
{
  "info": {
    "name": "Call Masking API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Generate Masked Call",
      "request": {
        "method": "POST",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/gateways/call/ABC12345/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["gateways", "call", "ABC12345", ""]
        }
      }
    },
    {
      "name": "Get Call Info",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/gateways/call/ABC12345/info/",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["gateways", "call", "ABC12345", "info", ""]
        }
      }
    }
  ]
}
```

Then import in Postman: File → Import → Select file
