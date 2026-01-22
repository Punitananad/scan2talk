# Razorpay Payment Gateway - Quick Reference

## 🚀 Quick Deploy

### Windows (PowerShell)
```powershell
.\deploy_razorpay.ps1
```

### Linux/Mac
```bash
chmod +x deploy_razorpay.sh
./deploy_razorpay.sh
```

## 🔑 Credentials

```bash
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026
```

## 🌐 URLs

| Purpose | URL |
|---------|-----|
| Recharge Page | https://scan2talk.in/accounts/wallet/recharge/ |
| Webhook | https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/ |
| Dashboard | https://dashboard.razorpay.com/ |

## 📋 Webhook Configuration

1. Go to: https://dashboard.razorpay.com/app/webhooks
2. Click **+ Add New Webhook**
3. Enter:
   - **URL**: `https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/`
   - **Secret**: `scan2talk_rzp_webhook_live_2026`
4. Select Events:
   - ✅ `payment.captured`
   - ✅ `payment.failed`
   - ✅ `order.paid`
5. Click **Create Webhook**

## 🧪 Test Payment

### Test Cards (Test Mode Only)
```
Card: 4111 1111 1111 1111
CVV: 123
Expiry: 12/25
```

### Test Flow
1. Login: https://scan2talk.in/accounts/login/
2. Go to Wallet: https://scan2talk.in/accounts/wallet/
3. Click "Recharge Wallet"
4. Enter amount (min ₹1)
5. Complete payment
6. Verify balance updated

## 🔍 Monitoring

### Check Logs
```bash
ssh root@68.183.91.15
tail -f /var/log/gunicorn/error.log | grep -i razorpay
```

### Check Orders
```python
from apps.accounts.wallet_models import RechargeOrder

# Pending orders
RechargeOrder.objects.filter(status='pending').order_by('-created_at')[:5]

# Completed orders
RechargeOrder.objects.filter(status='completed').order_by('-created_at')[:5]
```

## 🛠️ Troubleshooting

### Payment Not Completing
```bash
# Check Razorpay dashboard
# Check server logs
ssh root@68.183.91.15 "tail -100 /var/log/gunicorn/error.log"

# Check order status in database
python manage.py shell
>>> from apps.accounts.wallet_models import RechargeOrder
>>> order = RechargeOrder.objects.get(order_id='ORD...')
>>> print(order.status, order.gateway_order_id)
```

### Webhook Not Working
```bash
# Test webhook URL
curl -X POST https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check webhook logs in Razorpay dashboard
# Settings → Webhooks → View Logs
```

## 📊 Payment Flow

```
User → Recharge Page → Enter Amount → Create Order
  ↓
Razorpay API → Create Order → Get Order ID
  ↓
Redirect → Razorpay Checkout → User Pays
  ↓
Payment Success → Callback to Frontend → Verify Signature
  ↓
Call Success API → Verify Payment → Credit Wallet
  ↓
Webhook (Backup) → Verify Signature → Credit Wallet (if not done)
  ↓
Success Page → Show Balance
```

## 🔐 Security

- ✅ HTTPS only
- ✅ Signature verification on all payments
- ✅ Webhook signature verification
- ✅ CSRF protection
- ✅ Order ID validation
- ✅ Amount validation

## 📞 Support

- **Razorpay Support**: support@razorpay.com
- **Phone**: +91-80-61799111
- **Dashboard**: https://dashboard.razorpay.com/
- **Docs**: https://razorpay.com/docs/

## ✅ Checklist

- [ ] Code deployed to production
- [ ] .env file updated with credentials
- [ ] Webhook configured in Razorpay dashboard
- [ ] Test payment completed successfully
- [ ] Wallet balance updated correctly
- [ ] Transaction history shows recharge
- [ ] Webhook receiving events
- [ ] No errors in logs

---

**Status**: Ready for Production ✅
**Last Updated**: January 22, 2026
