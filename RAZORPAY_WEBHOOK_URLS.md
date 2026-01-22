# Razorpay/PhonePe Webhook URLs for scan2talk.in

## Current Payment Gateway: PhonePe

Your system is currently using **PhonePe** payment gateway, not Razorpay.

## Webhook URLs to Configure

### 1. Owner Wallet Recharge Callback
**URL**: `https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/`

**Purpose**: Handle payment callbacks when users recharge their wallet

**Methods**: POST, GET

**Events to Subscribe**:
- Payment Success
- Payment Failed
- Payment Pending

---

### 2. Visitor Payment Callback (Prepaid QR Codes)
**URL**: `https://scan2talk.in/api/v1/auth/wallet/visitor-pay/callback/`

**Purpose**: Handle payment callbacks when visitors pay to contact owners with ₹0 balance

**Methods**: POST, GET

**Events to Subscribe**:
- Payment Success
- Payment Failed
- Payment Pending

---

## If You Want to Use Razorpay Instead

If you want to switch from PhonePe to Razorpay, here are the webhook URLs you would need:

### Razorpay Webhook URL (Generic)
**URL**: `https://scan2talk.in/api/v1/auth/wallet/recharge/callback/`

**Purpose**: Generic payment callback handler

**Methods**: POST

**Events to Subscribe**:
- payment.captured
- payment.failed
- order.paid

---

## PhonePe Dashboard Configuration

### Step 1: Login to PhonePe Dashboard
1. Go to: https://www.phonepe.com/business/
2. Login with your credentials
3. Navigate to "Settings" → "Webhooks"

### Step 2: Add Webhook URLs

**For Owner Wallet Recharge:**
```
URL: https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/
Method: POST
Events: All Payment Events
```

**For Visitor Payments:**
```
URL: https://scan2talk.in/api/v1/auth/wallet/visitor-pay/callback/
Method: POST
Events: All Payment Events
```

### Step 3: Configure Webhook Secret
1. PhonePe will provide a webhook secret key
2. Add it to your `.env` file:
   ```bash
   PHONEPE_WEBHOOK_SECRET=your_webhook_secret_here
   ```

### Step 4: Test Webhooks
1. Use PhonePe's test mode
2. Make a test payment
3. Check if webhook is received
4. Verify payment status updates correctly

---

## Razorpay Dashboard Configuration (If Switching)

### Step 1: Login to Razorpay Dashboard
1. Go to: https://dashboard.razorpay.com/
2. Login with your credentials
3. Navigate to "Settings" → "Webhooks"

### Step 2: Add Webhook URL
```
URL: https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
Active Events:
  ✅ payment.captured
  ✅ payment.failed
  ✅ order.paid
  ✅ payment.authorized
```

### Step 3: Get Webhook Secret
1. Razorpay will generate a webhook secret
2. Copy the secret key
3. Add to `.env` file:
   ```bash
   RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here
   ```

### Step 4: Configure Razorpay Credentials
Add these to your `.env` file:
```bash
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

---

## Current URL Routes (From Your Code)

### Wallet Recharge Routes
```python
# Owner wallet recharge
path('wallet/recharge/', wallet_views.recharge_wallet, name='recharge_wallet')
path('wallet/recharge/success/', wallet_views.recharge_success, name='recharge_success')
path('wallet/recharge/cancel/', wallet_views.recharge_cancel, name='recharge_cancel')
path('wallet/phonepe/callback/', wallet_views.phonepe_callback, name='phonepe_callback')

# API routes
path('api/wallet/recharge/create/', wallet_views.CreateRechargeOrderAPI.as_view())
path('api/wallet/recharge/callback/', wallet_views.recharge_callback)
```

### Visitor Payment Routes
```python
# Visitor payment (when owner has ₹0)
path('wallet/visitor-pay/<str:identifier>/', wallet_views.initiate_visitor_payment)
path('wallet/visitor-pay/callback/', wallet_views.visitor_payment_callback)
path('wallet/visitor-pay/success/<str:order_id>/', wallet_views.visitor_payment_success)
path('wallet/visitor-pay/failed/', wallet_views.visitor_payment_failed)
```

---

## Webhook Payload Examples

### PhonePe Callback Payload
```json
{
  "merchantId": "M227BOU8BBNV7",
  "merchantTransactionId": "ORDER123456",
  "transactionId": "T2024012012345678",
  "amount": 10000,
  "state": "COMPLETED",
  "responseCode": "SUCCESS",
  "paymentInstrument": {
    "type": "UPI",
    "utr": "123456789012"
  }
}
```

### Razorpay Webhook Payload
```json
{
  "entity": "event",
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_xxxxxxxxxxxxx",
        "amount": 10000,
        "currency": "INR",
        "status": "captured",
        "order_id": "order_xxxxxxxxxxxxx",
        "method": "upi"
      }
    }
  }
}
```

---

## Testing Webhooks Locally

### Using ngrok (for local testing)
```bash
# Install ngrok
# Download from: https://ngrok.com/

# Start your Django server
python manage.py runserver

# In another terminal, start ngrok
ngrok http 8000

# Use the ngrok URL in webhook configuration
# Example: https://abc123.ngrok.io/api/v1/auth/wallet/phonepe/callback/
```

### Using Postman
```bash
# Test PhonePe callback
POST https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/
Content-Type: application/json

{
  "merchantTransactionId": "TEST_ORDER_123",
  "transactionId": "T123456789",
  "amount": 10000,
  "state": "COMPLETED",
  "responseCode": "SUCCESS"
}
```

---

## Security Considerations

### 1. Verify Webhook Signatures
Always verify the webhook signature to ensure it's from PhonePe/Razorpay:

```python
# In your callback handler
def verify_webhook_signature(request):
    signature = request.headers.get('X-PhonePe-Signature')
    # Verify signature using your webhook secret
    # Return True if valid, False otherwise
```

### 2. Use HTTPS Only
- ✅ Your domain uses HTTPS: `https://scan2talk.in`
- ✅ Webhooks are secure

### 3. Validate Order IDs
- Always check if order exists in your database
- Verify order amount matches payment amount
- Check order status before updating

### 4. Idempotency
- Handle duplicate webhook calls
- Check if payment is already processed
- Use transaction IDs to prevent double processing

---

## Troubleshooting

### Webhook Not Received
1. Check if URL is accessible: `curl https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/`
2. Verify webhook is configured in PhonePe dashboard
3. Check server logs: `tail -f /var/log/nginx/error.log`
4. Check Django logs for errors

### Payment Not Updating
1. Check webhook payload in logs
2. Verify signature validation
3. Check order ID matches
4. Review callback handler code

### Testing Failed
1. Use PhonePe test mode
2. Check test credentials in `.env`
3. Verify callback URL is correct
4. Check for CSRF token issues (use `@csrf_exempt`)

---

## Quick Reference

| Purpose | Webhook URL | Method |
|---------|-------------|--------|
| Owner Wallet Recharge | `https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/` | POST, GET |
| Visitor Payment | `https://scan2talk.in/api/v1/auth/wallet/visitor-pay/callback/` | POST, GET |
| Generic Callback | `https://scan2talk.in/api/v1/auth/wallet/recharge/callback/` | POST |

---

## Summary

✅ **Primary Webhook URL (PhonePe)**: 
```
https://scan2talk.in/api/v1/auth/wallet/phonepe/callback/
```

✅ **Visitor Payment Webhook URL**: 
```
https://scan2talk.in/api/v1/auth/wallet/visitor-pay/callback/
```

✅ **Alternative (Razorpay)**: 
```
https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
```

Configure these URLs in your payment gateway dashboard to receive payment notifications!
