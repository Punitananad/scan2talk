# Call Masking Quick Reference

## 🚀 Quick Start

### Test the Integration
```bash
python manage.py shell < test_call_masking.py
```

### Generate a Masked Call (Python)
```python
from apps.communications.call_masking_service import create_masked_call

result = create_masked_call('9876543210', 'QR-001')
print(result['call_url'])  # tel:01205019042,4821#
```

### Generate a Masked Call (API)
```bash
curl -X POST http://localhost:8000/gateways/call/ABC12345/
```

---

## 📡 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/gateways/call/<qr_code>/` | Generate masked call URL |
| GET | `/gateways/call/<qr_code>/info/` | Get call info (no PIN) |

---

## 🔑 Credentials

```
Username: 1090600
Password: agent007
DID: 01205019042
Portal: https://telephonycloud.co.in/portal/
```

---

## 📝 Response Format

```json
{
  "success": true,
  "pin": "4821",
  "call_url": "tel:01205019042,4821#",
  "did_number": "01205019042",
  "expires_in_minutes": 10
}
```

---

## 💻 Code Examples

### Django View
```python
from apps.communications.call_masking_service import create_masked_call_for_qr

result = create_masked_call_for_qr(qr_obj)
if result['success']:
    return JsonResponse(result)
```

### JavaScript
```javascript
const res = await fetch('/gateways/call/ABC12345/', {method: 'POST'});
const data = await res.json();
if (data.success) window.location.href = data.call_url;
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `apps/communications/adapters/call_masking_adapter.py` | API adapter |
| `apps/communications/call_masking_service.py` | Service layer |
| `apps/gateways/call_masking_views.py` | Django views |
| `CALL_MASKING_GUIDE.md` | Full documentation |
| `CALL_MASKING_API.md` | API reference |

---

## 🔧 Configuration

### .env
```bash
SPARKTG_USERNAME=1090600
SPARKTG_PASSWORD=agent007
SPARKTG_DID_NUMBER=01205019042
SPARKTG_SID=906
```

---

## 🎯 Integration

### Add to Template
```html
{% include 'gateways/call_button_snippet.html' %}
```

### Add to View Context
```python
context['call_masking_enabled'] = bool(settings.SPARKTG_USERNAME)
```

---

## 🐛 Debugging

### Check Logs
```bash
# Look for these messages
INFO: Call mask created: PIN=4821, QR=ABC12345
ERROR: SparkTG API error: ...
```

### Check Cache
```python
from django.core.cache import cache
cache.get('call_mask_pin_4821')
```

---

## ⚡ Common Issues

| Issue | Solution |
|-------|----------|
| "API request timeout" | Check network/credentials |
| "Owner phone not available" | Verify user has phone number |
| "Gateway not active" | Check gateway.is_active |
| Rate limit exceeded | Wait 1 hour or adjust limit |

---

## 📊 Flow

```
User Scans QR → Clicks Call → System Generates PIN → 
SparkTG Maps PIN → Returns tel: URL → User Dials → 
Call Connects → PIN Expires (10 min)
```

---

## ✅ Checklist

- [x] Implementation complete
- [x] Server running without errors
- [ ] Test with real phone number
- [ ] Add to production templates
- [ ] Monitor API usage

---

## 📞 Support

- **Docs:** `CALL_MASKING_GUIDE.md`
- **API:** `CALL_MASKING_API.md`
- **SparkTG:** navodit@sparktg.com
