# Distributor Category - Quick Start Guide

## What is Distributor Category?

A special QR category that requires **one-time payment** before activation, then works like Free category forever.

## Flow Summary

```
Scan QR → Pay Once → Activate → Use Forever (Free)
```

## Setup Steps

### 1. Run Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Distributor Category (Admin)

Go to: **Admin Dashboard → Manage Categories → Add Category**

**Settings:**
- **Name:** Distributor
- **Type:** Distributor - One-Time Payment
- **Activation Fee:** ₹500 (or your amount)
- **Message Cost:** 0.00
- **Call Cost:** 0.00
- **Free Limits:** 0 (unlimited)
- **Active:** ✓

### 3. Generate QR Batch

Go to: **Generate QR Codes**

- **Quantity:** 10 (or any number)
- **Batch Name:** DIST-BATCH-001
- **Category:** Select "Distributor"
- Click **Generate**

### 4. Test the Flow

#### Option A: Manual Test
1. Get a QR code from the batch
2. Visit: `/gateways/activate/[QR_CODE]/`
3. Should redirect to payment page
4. Complete payment
5. Proceed with activation

#### Option B: Automated Test
```bash
python test_distributor_category.py
```

## User Journey

### Step 1: Scan QR Code
User scans the QR tag on their vehicle

### Step 2: Payment Page
- Shows QR code details
- Shows activation fee (e.g., ₹500)
- Shows benefits:
  - ✓ Lifetime activation
  - ✓ Free unlimited usage
  - ✓ No recurring charges
  - ✓ No wallet recharge needed

### Step 3: Make Payment
- Click "Pay ₹500 & Activate"
- Redirected to PhonePe
- Complete payment

### Step 4: Activation
After successful payment:
- **Step 1:** Enter phone number
- **Step 2:** Verify OTP
- **Step 3:** Enter vehicle details
- **Success:** QR activated!

### Step 5: Use Forever
- Works exactly like Free category
- Unlimited messages and calls
- No wallet deductions
- No recharge needed

## Key Features

### ✅ One-Time Payment
- Pay only once during activation
- No recurring charges
- No subscription fees

### ✅ Unlimited Usage
- Free messages (unlimited)
- Free calls (unlimited)
- No per-use charges

### ✅ No Wallet Management
- No wallet recharge needed
- No balance checking
- No credit deductions

### ✅ Lifetime Validity
- Once activated, works forever
- No expiration
- No renewal needed

## Admin Features

### View Payments
**Admin → Distributor Payments**

See all one-time payments:
- QR code
- Amount paid
- Payment status
- Phone number
- Payment date

### Manual Actions
- Mark payment as completed (if needed)
- Mark payment as failed
- View payment details

### Category Management
- Set activation fee
- Enable/disable category
- Track QR codes by category

## URLs

### Payment Page
```
/accounts/distributor-payment/[QR_CODE]/
```

### Payment Callback
```
/accounts/distributor-payment-callback/[QR_CODE]/
```

### Activation Page
```
/gateways/activate/[QR_CODE]/
```

## Database Tables

### distributor_payments
Tracks one-time activation payments

**Fields:**
- qr_code (OneToOne)
- amount
- order_id
- gateway_payment_id
- status (pending/completed/failed)
- phone
- paid_at

### recharge_categories
Added field: `distributor_activation_fee`

## Payment Gateway

Uses **PhonePe** for payments:
- Secure payment processing
- Instant verification
- Automatic callback handling

## Troubleshooting

### Payment successful but activation blocked
**Solution:** Check payment status in admin, manually mark as completed if needed

### Payment page not showing
**Solution:** 
1. Verify category type is 'distributor'
2. Check activation_fee is set
3. Ensure QR has category assigned

### Activation working without payment
**Solution:** Check the payment verification logic in `activate_qr_code()` view

### Wallet deducting credits
**Solution:** Verify QRWallet methods include distributor category checks

## Comparison with Other Categories

| Feature | Free | Prepaid | Distributor |
|---------|------|---------|-------------|
| Initial Cost | ₹0 | ₹0 | ₹500 (one-time) |
| Activation | Direct | Direct | After payment |
| Usage Cost | Free | Pay per use | Free |
| Wallet | No | Yes | No |
| Recharge | No | Yes | No |
| Best For | Testing | Regular users | Distributors |

## Benefits for Distributors

1. **Simple Pricing:** One-time fee, no surprises
2. **No Maintenance:** No wallet management needed
3. **Unlimited Usage:** Use as much as needed
4. **Easy Onboarding:** Simple payment + activation
5. **Lifetime Value:** Pay once, use forever

## Testing Checklist

- [ ] Migration applied
- [ ] Category created with fee
- [ ] QR batch generated
- [ ] Payment page loads
- [ ] Payment processes successfully
- [ ] Callback updates status
- [ ] Activation proceeds after payment
- [ ] QR works after activation
- [ ] Messages send without deduction
- [ ] Calls work without deduction
- [ ] Admin can view payments

## Support

For issues or questions:
1. Check logs: `logs/` directory
2. Check payment status in admin
3. Verify PhonePe configuration
4. Test with test_distributor_category.py

## Summary

The Distributor category provides a **pay-once-use-forever** model:
- ✅ One-time activation payment
- ✅ Unlimited free usage after payment
- ✅ No wallet or recharge management
- ✅ Perfect for distributor business model

**Implementation is complete and ready to use!**
