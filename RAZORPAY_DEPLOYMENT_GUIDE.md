# Razorpay Payment Gateway - Deployment Guide

## Overview
Razorpay payment gateway is now integrated for wallet recharge functionality. This guide covers deployment and configuration.

## Current Status
✅ Razorpay service implemented (`apps/accounts/razorpay_service.py`)
✅ Checkout page created (`templates/accounts/razorpay_checkout.html`)
✅ URL routes configured
✅ Wallet views updated to use Razorpay
✅ Webhook handler implemented
✅ Package installed (`razorpay==1.4.1`)

## Environment Variables

### Already Added to .env
```bash
# Razorpay Payment Gateway Configuration
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026
```

### Settings Configuration
The following is already configured in `gateway_platform/settings.py`:
```python
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_WEBHOOK_SECRET = env('RAZORPAY_WEBHOOK_SECRET', default='')
```

## Deployment Steps

### 1. Update Production .env File
SSH into your production server and update the .env file:

```bash
ssh root@68.183.91.15

# Navigate to project directory
cd /root/CPA

# Edit .env file
nano .env

# Add/Update these lines:
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026

# Save and exit (Ctrl+X, Y, Enter)
```

### 2. Deploy Code Changes
From your Windows machine, push the changes:

```powershell
# Add all changes
git add .

# Commit
git commit -m "Add Razorpay payment gateway integration"

# Push to repository
git push origin main
```

### 3. Pull Changes on Server
```bash
# On production server
cd /root/CPA
git pull origin main

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 4. Configure Razorpay Webhook

#### Webhook URL
```
https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/
```

#### Steps to Configure in Razorpay Dashboard:
1. Login to Razorpay Dashboard: https://dashboard.razorpay.com/
2. Go to **Settings** → **Webhooks**
3. Click **+ Add New Webhook**
4. Enter Webhook URL: `https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/`
5. Enter Webhook Secret: `scan2talk_rzp_webhook_live_2026`
6. Select Events to Listen:
   - ✅ `payment.captured`
   - ✅ `payment.failed`
   - ✅ `order.paid`
7. Set Status: **Active**
8. Click **Create Webhook**

## Testing

### Test Recharge Flow

1. **Login to Application**
   ```
   https://scan2talk.in/accounts/login/
   ```

2. **Navigate to Wallet**
   ```
   https://scan2talk.in/accounts/wallet/
   ```

3. **Click "Recharge Wallet"**
   ```
   https://scan2talk.in/accounts/wallet/recharge/
   ```

4. **Enter Amount and Submit**
   - Minimum: ₹1
   - You'll be redirected to Razorpay checkout page

5. **Complete Payment**
   - Use Razorpay test cards (if in test mode)
   - Or real payment (if in live mode)

### Test Cards (Test Mode Only)
```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
```

### Verify Payment Success
1. After payment, you should be redirected to success page
2. Check wallet balance is updated
3. Check transaction history

## API Endpoints

### Recharge Wallet (Web)
```
POST /api/v1/auth/wallet/recharge/
Form Data: { amount: 100 }
```

### Razorpay Checkout
```
GET /api/v1/auth/wallet/razorpay/checkout/?order_id=<ORDER_ID>
```

### Payment Success Callback
```
POST /api/v1/auth/wallet/razorpay/success/
Body: {
  razorpay_payment_id: "pay_xxx",
  razorpay_order_id: "order_xxx",
  razorpay_signature: "signature_xxx"
}
```

### Webhook (Server-to-Server)
```
POST /api/v1/auth/wallet/razorpay/webhook/
Headers: {
  X-Razorpay-Signature: "webhook_signature"
}
Body: {
  event: "payment.captured",
  payload: { ... }
}
```

## Payment Flow

### User Journey
1. User clicks "Recharge Wallet"
2. Enters amount (minimum ₹1)
3. System creates `RechargeOrder` with status `pending`
4. Razorpay order is created via API
5. User is redirected to Razorpay checkout page
6. User completes payment
7. Razorpay sends callback to frontend
8. Frontend verifies signature and calls success endpoint
9. Backend verifies payment and credits wallet
10. User is redirected to success page

### Webhook Flow (Backup)
1. Razorpay sends webhook to server
2. Server verifies webhook signature
3. Server processes payment event
4. Wallet is credited (if not already done)

## Security Features

### Payment Signature Verification
- All payments are verified using Razorpay signature
- Prevents tampering and fraud

### Webhook Signature Verification
- Webhooks are verified using HMAC-SHA256
- Only authentic Razorpay webhooks are processed

### HTTPS Only
- All payment URLs use HTTPS
- Secure data transmission

## Monitoring

### Check Payment Logs
```bash
# On production server
tail -f /var/log/gunicorn/error.log | grep -i razorpay
```

### Check Razorpay Dashboard
- Login to Razorpay Dashboard
- Go to **Transactions** → **Payments**
- View all payment attempts and statuses

### Database Queries
```python
# Check recent orders
from apps.accounts.wallet_models import RechargeOrder
RechargeOrder.objects.filter(status='pending').order_by('-created_at')[:10]

# Check completed orders
RechargeOrder.objects.filter(status='completed').order_by('-created_at')[:10]
```

## Troubleshooting

### Payment Not Completing
1. Check Razorpay dashboard for payment status
2. Check server logs for errors
3. Verify webhook is configured correctly
4. Check if signature verification is passing

### Webhook Not Working
1. Verify webhook URL is accessible: `https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/`
2. Check webhook secret matches in .env
3. Check Razorpay dashboard webhook logs
4. Verify CSRF exemption is working

### Balance Not Updating
1. Check if order status is `completed`
2. Check wallet transaction history
3. Verify `mark_completed()` method is called
4. Check for any exceptions in logs

## Quick Deploy Commands

### From Windows (PowerShell)
```powershell
# Commit and push
git add .
git commit -m "Update Razorpay configuration"
git push origin main

# Deploy to production
ssh root@68.183.91.15 "cd /root/CPA && git pull origin main && sudo systemctl restart gunicorn"
```

### From Linux/Mac
```bash
# Commit and push
git add .
git commit -m "Update Razorpay configuration"
git push origin main

# Deploy to production
ssh root@68.183.91.15 "cd /root/CPA && git pull origin main && sudo systemctl restart gunicorn"
```

## Support

### Razorpay Support
- Email: support@razorpay.com
- Phone: +91-80-61799111
- Dashboard: https://dashboard.razorpay.com/

### Documentation
- Razorpay API Docs: https://razorpay.com/docs/api/
- Checkout Integration: https://razorpay.com/docs/payment-gateway/web-integration/standard/
- Webhooks: https://razorpay.com/docs/webhooks/

## Notes

- **Live Mode**: Currently using live credentials (`rzp_live_xxx`)
- **Test Mode**: To use test mode, replace with test credentials (`rzp_test_xxx`)
- **Minimum Amount**: ₹1 (100 paise)
- **Currency**: INR only
- **Credits**: 1 rupee = 1 call credit

## Success Indicators

✅ User can initiate recharge
✅ Razorpay checkout page loads
✅ Payment can be completed
✅ Wallet balance updates after payment
✅ Transaction history shows recharge
✅ Webhook receives payment events
✅ No errors in server logs

---

**Last Updated**: January 22, 2026
**Status**: Ready for Production Deployment
