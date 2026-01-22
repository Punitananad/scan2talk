# Razorpay Integration for QR Code Payments

## ✅ What Was Changed

The system has been updated to use **Razorpay** as the payment gateway for all wallet recharges, including QR code purchases. The test payment page has been replaced with real Razorpay integration.

## 🔧 Changes Made

### 1. **Wallet Service Updated** (`apps/accounts/wallet_service.py`)
- Removed test mode logic
- Now directly uses `RazorpayGatewayService` for all payments
- No more test payment URLs

### 2. **Environment Variables** (`.env`)
Your Razorpay credentials are already configured:
```env
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026
```

### 3. **Settings** (`gateway_platform/settings.py`)
Razorpay settings are loaded from environment variables:
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `RAZORPAY_WEBHOOK_SECRET`

## 🚀 How It Works Now

### User Flow:
1. User clicks **"Get Your QR Code"** (or recharges wallet)
2. System creates a Razorpay order
3. User is redirected to Razorpay checkout page
4. User completes payment via Razorpay
5. Payment is verified and wallet is credited
6. User can proceed with QR generation

### Payment Flow:
```
User Request → Create Order → Razorpay Order Created → Checkout Page → Payment → Webhook/Callback → Wallet Credited
```

## 📋 What's Already Set Up

✅ Razorpay service (`apps/accounts/razorpay_service.py`)
✅ Razorpay checkout template (`templates/accounts/razorpay_checkout.html`)
✅ Webhook handler (`/api/v1/auth/wallet/recharge/callback/`)
✅ Payment success handler
✅ Razorpay Python SDK (`razorpay==1.4.1` in requirements.txt)
✅ Environment variables configured

## 🔐 Security Features

- Payment signature verification
- Webhook signature verification
- CSRF protection
- Secure order ID generation

## 🧪 Testing

To test the integration:

1. **Wallet Recharge:**
   - Go to `/api/v1/auth/wallet/recharge/`
   - Enter amount
   - Complete payment via Razorpay

2. **QR Code Purchase:**
   - Admin generates QR codes (no payment needed for admin)
   - Users activate QR codes (free activation)
   - Wallet recharge uses Razorpay when needed

## 📝 Important Notes

- **Test Mode Removed:** The old `RECHARGE_TEST_MODE` setting is now ignored
- **Live Credentials:** You're using live Razorpay credentials (`rzp_live_...`)
- **Webhook URL:** Configure in Razorpay Dashboard:
  ```
  https://scan2talk.in/api/v1/auth/wallet/recharge/callback/
  ```
- **Webhook Secret:** Must match the one in your `.env` file

## 🔄 Webhook Configuration

In your Razorpay Dashboard:
1. Go to Settings → Webhooks
2. Add webhook URL: `https://scan2talk.in/api/v1/auth/wallet/recharge/callback/`
3. Select events:
   - `payment.captured`
   - `payment.failed`
   - `order.paid`
4. Use the webhook secret from your `.env` file

## 💡 Key Files

- **Service:** `apps/accounts/razorpay_service.py`
- **Views:** `apps/accounts/wallet_views.py`
- **Wallet Service:** `apps/accounts/wallet_service.py`
- **Template:** `templates/accounts/razorpay_checkout.html`
- **Settings:** `gateway_platform/settings.py`
- **Environment:** `.env`

## ✨ Benefits

- Real payment processing
- Secure and PCI compliant
- Multiple payment methods (cards, UPI, wallets, netbanking)
- Automatic refunds support
- Transaction tracking
- Webhook notifications

---

**Status:** ✅ Razorpay integration is now active and ready for production use!
