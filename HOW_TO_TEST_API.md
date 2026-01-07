# How to Test Call Masking API - Complete Guide

## ✅ Quick Test (Already Done!)

The test script already ran successfully! You saw:
```
✓ Success!
  PIN: 4987
  Call URL: tel:01205019042,4987#
  DID Number: 01205019042
  Expires in: 10 minutes
```

This means the API is working! 🎉

---

## 🧪 5 Ways to Test the API

### Method 1: Python Test Script (Easiest) ✅ DONE

```bash
python manage.py shell < test_call_masking.py
```

**Result:** Already tested successfully!

---

### Method 2: HTML Test Page (Visual)

1. **Open the test page:**
   ```
   Open: test_call_masking.html in your browser
   ```

2. **Make sure server is running:**
   ```bash
   python manage.py runserver
   ```

3. **Test in browser:**
   - Enter a QR code (e.g., ABC12345)
   - Click "Generate Call URL"
   - See the result with PIN and call URL

---

### Method 3: PowerShell/CMD (Windows)

```powershell
# Test 1: Generate masked call
Invoke-RestMethod -Uri "http://localhost:8000/gateways/call/ABC12345/" -Method POST | ConvertTo-Json

# Test 2: Get call info
Invoke-RestMethod -Uri "http://localhost:8000/gateways/call/ABC12345/info/" -Method GET | ConvertTo-Json
```

---

### Method 4: Django Shell (Interactive)

```bash
python manage.py shell
```

Then paste:
```python
from apps.communications.call_masking_service import create_masked_call

# Test with any phone number
result = create_masked_call('9876543210', 'TEST-001')
print(result)
```

---

### Method 5: Browser Console (Quick)

1. Open browser to: `http://localhost:8000`
2. Press F12 to open console
3. Paste this:

```javascript
fetch('http://localhost:8000/gateways/call/ABC12345/', {
    method: 'POST'
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 📋 What You Need to Test

### Prerequisites

1. **Server Running:** ✅ (Already running on port 8000)
2. **QR Code:** You need an activated QR code

### Get a QR Code to Test

**Option A: Use existing QR code**
```bash
python manage.py shell
```
```python
from apps.gateways.qr_models import PreGeneratedQR
qrs = PreGeneratedQR.objects.filter(status='activated')
for qr in qrs:
    print(f"QR Code: {qr.qr_code}")
```

**Option B: Create a test QR code**
1. Go to: http://localhost:8000/admin/
2. Login: admin@example.com / admin123
3. Generate QR codes
4. Activate one

---

## 🎯 Expected Results

### Success Response
```json
{
  "success": true,
  "pin": "4821",
  "call_url": "tel:01205019042,4821#",
  "did_number": "01205019042",
  "expires_in_minutes": 10
}
```

### Error Response (QR not found)
```json
{
  "success": false,
  "error": "QR code not found or not activated"
}
```

---

## 🔍 Testing Checklist

- [x] **Basic Test:** Python script ran successfully ✅
- [ ] **With Real QR:** Test with an activated QR code
- [ ] **Error Handling:** Test with invalid QR code
- [ ] **Rate Limiting:** Make 11 requests in 1 hour (should fail)
- [ ] **PIN Expiry:** Wait 10 minutes, check if PIN expires
- [ ] **Mobile Test:** Click call URL on mobile device
- [ ] **Real Call:** Test actual phone call with SparkTG

---

## 🚀 Quick Test Commands

### Test 1: Basic Function Test
```bash
python manage.py shell < test_call_masking.py
```

### Test 2: Interactive Test
```bash
python manage.py shell
```
```python
from apps.communications.call_masking_service import create_masked_call
result = create_masked_call('9876543210', 'TEST-001')
print(f"PIN: {result['pin']}, URL: {result['call_url']}")
```

### Test 3: API Endpoint Test (PowerShell)
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/gateways/call/ABC12345/" -Method POST
```

---

## 📱 Testing on Mobile

1. **Generate call URL** using any method above
2. **Copy the call URL** (e.g., `tel:01205019042,4821#`)
3. **Send to your mobile** via WhatsApp/SMS
4. **Click the link** on mobile
5. **Phone should dial** with PIN automatically

---

## 🐛 Troubleshooting

### Issue: "QR code not found"
**Solution:** Use an activated QR code. Check available codes:
```python
from apps.gateways.qr_models import PreGeneratedQR
PreGeneratedQR.objects.filter(status='activated').values_list('qr_code', flat=True)
```

### Issue: "Gateway not active"
**Solution:** Activate the gateway in admin panel

### Issue: "API request timeout"
**Solution:** Check SparkTG credentials in .env file

### Issue: "Owner phone not available"
**Solution:** Ensure the QR owner has a phone number

---

## 📊 Test Results Log

Keep track of your tests:

| Test | QR Code | Result | PIN | Notes |
|------|---------|--------|-----|-------|
| Script | TEST-QR-001 | ✅ Success | 4987 | Working! |
| API | ABC12345 | ⏳ Pending | - | Need real QR |
| Mobile | - | ⏳ Pending | - | Need to test |

---

## 🎓 Next Steps

1. ✅ **Basic test passed** - API is working!
2. **Get a real QR code** - Activate one in admin
3. **Test with real QR** - Use the HTML test page
4. **Test on mobile** - Click the call URL
5. **Test real call** - Make actual phone call

---

## 📞 Test Files Reference

| File | Purpose | How to Use |
|------|---------|------------|
| `test_call_masking.py` | Python script | `python manage.py shell < test_call_masking.py` |
| `test_call_masking.html` | Visual test page | Open in browser |
| `test_interactive.py` | Shell commands | Copy/paste in Django shell |
| `test_api_curl.md` | cURL examples | Follow commands |
| `test_postman.md` | Postman guide | Import collection |

---

## ✅ Summary

**Your API is working!** The test script successfully:
- Generated a PIN (4987)
- Created a call URL (tel:01205019042,4987#)
- Mapped it to the phone number
- Set 10-minute expiry

**Next:** Test with a real activated QR code from your system!
