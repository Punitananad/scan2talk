# Razorpay Webhook URL Configuration

## 🔗 Webhook URL for Razorpay

```
https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
```

---

## 📋 Razorpay Dashboard Setup

### Step 1: Login to Razorpay Dashboard
1. Go to: **https://dashboard.razorpay.com/**
2. Login with your credentials
3. Navigate to **Settings** → **Webhooks**

### Step 2: Create New Webhook
1. Click **"+ Add New Webhook"**
2. Enter webhook URL:
   ```
   https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
   ```

### Step 3: Select Events
Select these events:
- ✅ **payment.authorized**
- ✅ **payment.captured**
- ✅ **payment.failed**
- ✅ **order.paid**

### Step 4: Save and Get Secret
1. Click **"Create Webhook"**
2. Razorpay will generate a **Webhook Secret**
3. Copy the secret (format: `whsec_xxxxxxxxxxxxx`)
4. Save it securely

---

## 🔐 Configure Webhook Secret

Add the webhook secret to your `.env` file on the server:

```bash
# SSH into server
ssh ramban@103.127.29.78

# Edit .env file
cd /home/ramban/gateway_platform
nano .env

# Add this line (replace with your actual secret)
RAZORPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# Save and exit (Ctrl+X, Y, Enter)

# Restart server
sudo systemctl restart gunicorn
```

---

## 🔑 Razorpay API Credentials

Also add your Razorpay API credentials to `.env`:

```bash
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Where to find these:**
1. Login to Razorpay Dashboard
2. Go to **Settings** → **API Keys**
3. Copy **Key ID** and **Key Secret**

---

## 📡 Webhook Payload Example

When a payment is successful, Razorpay will send this to your webhook:

```json
{
  "entity": "event",
  "account_id": "acc_xxxxxxxxxxxxx",
  "event": "payment.captured",
  "contains": ["payment"],
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_xxxxxxxxxxxxx",
        "entity": "payment",
        "amount": 10000,
        "currency": "INR",
        "status": "captured",
        "order_id": "order_xxxxxxxxxxxxx",
        "invoice_id": null,
        "international": false,
        "method": "upi",
        "amount_refunded": 0,
        "refund_status": null,
        "captured": true,
        "description": "Wallet Recharge",
        "card_id": null,
        "bank": null,
        "wallet": null,
        "vpa": "user@paytm",
        "email": "user@example.com",
        "contact": "+919876543210",
        "customer_id": "cust_xxxxxxxxxxxxx",
        "notes": [],
        "fee": 236,
        "tax": 36,
        "error_code": null,
        "error_description": null,
        "error_source": null,
        "error_step": null,
        "error_reason": null,
        "acquirer_data": {
          "rrn": "123456789012"
        },
        "created_at": 1704067200
      }
    }
  },
  "created_at": 1704067200
}
```

---

## 🧪 Test Webhook

### Option 1: Use Razorpay Test Mode
1. Switch to **Test Mode** in Razorpay Dashboard
2. Use test API keys (start with `rzp_test_`)
3. Make a test payment
4. Check if webhook is received

### Option 2: Manual Test with cURL
```bash
curl -X POST https://scan2talk.in/api/v1/auth/wallet/recharge/callback/ \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: test_signature" \
  -d '{
    "entity": "event",
    "event": "payment.captured",
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_test123",
          "amount": 10000,
          "currency": "INR",
          "status": "captured",
          "order_id": "order_test123",
          "method": "upi"
        }
      }
    }
  }'
```

### Option 3: Use Razorpay Webhook Tester
1. Go to Razorpay Dashboard → Webhooks
2. Click on your webhook
3. Click **"Send Test Webhook"**
4. Select event type
5. Click **"Send"**

---

## ✅ Verify Webhook is Working

### Check Server Logs
```bash
# SSH into server
ssh ramban@103.127.29.78

# Check Django logs
cd /home/ramban/gateway_platform
tail -f logs/django.log

# Or check gunicorn logs
sudo journalctl -u gunicorn -f
```

### Check Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Test Payment Flow
1. Login to your app
2. Go to Wallet → Recharge
3. Make a test payment (₹1)
4. Check if balance updates
5. Check webhook logs

---

## 🔒 Security Best Practices

### 1. Always Verify Webhook Signature
Your code should verify the signature:
```python
import hmac
import hashlib

def verify_razorpay_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

### 2. Use HTTPS Only
✅ Your domain already uses HTTPS: `https://scan2talk.in`

### 3. Validate Webhook Data
- Check if order exists in database
- Verify amount matches
- Check payment status
- Prevent duplicate processing

### 4. Handle Idempotency
- Use payment ID to track processed payments
- Don't process same payment twice
- Log all webhook calls

---

## 🐛 Troubleshooting

### Webhook Not Received
**Check:**
1. ✅ URL is correct: `https://scan2talk.in/api/v1/auth/wallet/recharge/callback/`
2. ✅ Server is running: `sudo systemctl status gunicorn`
3. ✅ Firewall allows HTTPS: Port 443 open
4. ✅ Webhook is active in Razorpay Dashboard

**Test URL:**
```bash
curl -I https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
```

### Payment Not Updating
**Check:**
1. Webhook signature verification
2. Order ID exists in database
3. Payment status is "captured"
4. No errors in logs

### Signature Verification Failed
**Check:**
1. Webhook secret is correct in `.env`
2. Secret matches Razorpay Dashboard
3. Signature header is present: `X-Razorpay-Signature`

---

## 📞 Support

### Razorpay Support
- **Email**: support@razorpay.com
- **Phone**: +91-80-6890-6890
- **Docs**: https://razorpay.com/docs/webhooks/

### Your Webhook URL
```
https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
```

---

## 📝 Quick Checklist

Before going live, verify:

- [ ] Webhook URL added in Razorpay Dashboard
- [ ] Events selected: payment.captured, payment.failed, order.paid
- [ ] Webhook secret copied and added to `.env`
- [ ] API credentials (Key ID & Secret) added to `.env`
- [ ] Server restarted after `.env` changes
- [ ] Test payment successful
- [ ] Webhook received and processed
- [ ] Balance updated correctly
- [ ] Logs show no errors

---

## 🎉 Summary

**Your Razorpay Webhook URL:**
```
https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
```

**Add this URL to:**
- Razorpay Dashboard → Settings → Webhooks

**Select Events:**
- payment.authorized
- payment.captured  
- payment.failed
- order.paid

**Don't forget to:**
1. Copy webhook secret
2. Add to `.env` file
3. Restart server
4. Test with a payment

That's it! Your webhook is ready to receive payment notifications from Razorpay! 🚀
