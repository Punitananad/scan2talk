# 🚀 Quick Razorpay Setup Guide

## ✅ What's Done

Your system now uses **Razorpay** for all payments. The test payment page has been removed from the flow.

## 🔑 Your Credentials (Already in `.env`)

```env
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026
```

## ⚙️ One-Time Webhook Setup

Go to your Razorpay Dashboard and configure:

1. **URL:** `https://scan2talk.in/api/v1/auth/wallet/recharge/callback/`
2. **Secret:** `scan2talk_rzp_webhook_live_2026`
3. **Events:**
   - ✅ payment.captured
   - ✅ payment.failed
   - ✅ order.paid

## 🧪 Test It

1. Login to your app
2. Go to wallet recharge
3. Enter amount (₹1 minimum)
4. Complete payment via Razorpay
5. Wallet gets credited automatically

## 📝 What Changed

**Before:**
```
User → Create Order → Test Payment Page → Simulate Payment → Wallet Credit
```

**Now:**
```
User → Create Order → Razorpay Checkout → Real Payment → Wallet Credit
```

## 🎯 Key Points

- ✅ Using **live** Razorpay credentials (`rzp_live_...`)
- ✅ Test mode is **disabled**
- ✅ All payments are **real transactions**
- ✅ Supports cards, UPI, wallets, netbanking
- ✅ Automatic webhook notifications
- ✅ Payment signature verification

## 📂 Modified Files

- `apps/accounts/wallet_service.py` (Line 142-146)

## 🎉 Status

**LIVE AND READY!** Your payment system is now using Razorpay for all transactions.

---

**Need Help?** Check `RAZORPAY_QR_PAYMENT_INTEGRATION.md` for detailed documentation.
