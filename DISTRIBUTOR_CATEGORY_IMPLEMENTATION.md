# Distributor Category - Pay-Once-Then-Free Implementation

## Overview
The Distributor category is a new QR code category type that requires a **one-time activation payment** before the QR can be activated. After payment, it works exactly like the "Free - No Recharge Needed" category with unlimited usage.

## Key Features

### 1. One-Time Payment Model
- User scans QR code → Redirected to payment page
- Payment required before activation
- After successful payment → Proceed to normal activation flow
- No recurring charges or wallet recharge needed

### 2. Post-Payment Behavior
- Works exactly like "Free" category
- Unlimited messages and calls
- No wallet deductions
- No usage limits

## Implementation Details

### Database Changes

#### 1. RechargeCategory Model
**File:** `apps/accounts/recharge_models.py`

Added new category type:
```python
CATEGORY_TYPES = [
    ('free', 'Free - No Recharge Needed'),
    ('prepaid', 'Prepaid - Recharge Required'),
    ('postpaid', 'Postpaid - Bill Later'),
    ('trial', 'Trial - Limited Free Usage'),
    ('distributor', 'Distributor - One-Time Payment'),  # NEW
]
```

Added activation fee field:
```python
distributor_activation_fee = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    default=0.00,
    help_text="One-time payment for distributor category activation"
)
```

#### 2. DistributorPayment Model
**File:** `apps/accounts/recharge_models.py`

New model to track one-time payments:
```python
class DistributorPayment(BaseModel):
    qr_code = OneToOneField(PreGeneratedQR)
    amount = DecimalField
    order_id = CharField (unique)
    gateway_order_id = CharField
    gateway_payment_id = CharField
    status = CharField (pending/completed/failed)
    phone = CharField
    paid_at = DateTimeField
```

### Flow Implementation

#### 1. QR Activation Flow
**File:** `apps/gateways/qr_views.py`

Modified `activate_qr_code()` view:
```python
# Check if distributor category
if qr.category.category_type == 'distributor':
    # Check if payment completed
    try:
        payment = DistributorPayment.objects.get(qr_code=qr)
        if payment.status != 'completed':
            # Redirect to payment page
            return redirect('accounts:distributor_payment', qr_code=qr.qr_code)
    except DistributorPayment.DoesNotExist:
        # No payment - redirect to payment page
        return redirect('accounts:distributor_payment', qr_code=qr.qr_code)

# If payment completed, continue with normal activation
```

#### 2. Payment Views
**File:** `apps/accounts/wallet_views.py`

**New Views:**
- `distributor_payment(request, qr_code)` - Payment page
- `distributor_payment_callback(request, qr_code)` - Payment callback

**Payment Flow:**
1. User lands on payment page
2. Shows QR code, category, and activation fee
3. User clicks "Pay & Activate"
4. Creates DistributorPayment record
5. Redirects to PhonePe payment gateway
6. After payment, callback verifies status
7. If successful → Redirect to activation step 1
8. If failed → Show error and retry option

#### 3. URL Routes
**File:** `apps/accounts/urls.py`

Added routes:
```python
path('distributor-payment/<str:qr_code>/', wallet_views.distributor_payment, name='distributor_payment'),
path('distributor-payment-callback/<str:qr_code>/', wallet_views.distributor_payment_callback, name='distributor_payment_callback'),
```

### Wallet Logic Updates

#### QRWallet Methods
**File:** `apps/accounts/recharge_models.py`

Updated methods to handle distributor category:

**can_send_message():**
```python
if self.category.category_type == 'distributor':
    return True, "Distributor - unlimited messages"
```

**can_make_call():**
```python
if self.category.category_type == 'distributor':
    return True, "Distributor - unlimited calls"
```

**deduct_message_credit():**
```python
if self.category.category_type == 'distributor':
    self.total_messages_sent += 1
    self.save()
    return  # No deduction
```

**deduct_call_minutes():**
```python
if self.category.category_type == 'distributor':
    self.total_calls_made += 1
    self.total_call_duration += (minutes * 60)
    self.save()
    return  # No deduction
```

## User Experience Flow

### Complete Journey

```
1. User scans QR code
   ↓
2. System checks category type
   ↓
3. If Distributor → Check payment status
   ↓
4. If NOT paid → Redirect to payment page
   ↓
5. User sees:
   - QR code details
   - Activation fee amount
   - Benefits (lifetime, no recharge, unlimited usage)
   ↓
6. User clicks "Pay ₹X & Activate"
   ↓
7. Redirected to PhonePe payment
   ↓
8. After successful payment → Callback
   ↓
9. Payment marked as completed
   ↓
10. Redirect to activation Step 1 (Phone)
    ↓
11. Normal activation flow:
    - Step 1: Enter phone number
    - Step 2: Verify OTP
    - Step 3: Enter vehicle details
    ↓
12. QR activated successfully
    ↓
13. Works like Free category forever
```

## Admin Setup

### Creating Distributor Category

1. Go to Admin Dashboard
2. Navigate to "Manage Categories"
3. Create new category:
   - **Name:** "Distributor"
   - **Category Type:** "Distributor - One-Time Payment"
   - **Activation Fee:** Set amount (e.g., ₹500)
   - **Message Cost:** 0.00 (not used)
   - **Call Cost:** 0.00 (not used)
   - **Free Limits:** 0 (unlimited)

### Assigning to QR Batch

1. Generate QR batch
2. Select "Distributor" category
3. All QR codes in batch will require payment before activation

## Templates

### distributor_payment.html
**Location:** `templates/accounts/distributor_payment.html`

**Features:**
- Clean, modern design
- Shows QR code and category
- Large activation fee display
- Benefits list (lifetime, unlimited, no recharge)
- Secure payment button
- Payment status indicators
- Mobile-responsive

## Database Migration

Run migration to add new fields:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Migration adds:**
- `distributor_activation_fee` field to RechargeCategory
- `DistributorPayment` table

## Testing Checklist

### 1. Category Creation
- [ ] Create Distributor category in admin
- [ ] Set activation fee (e.g., ₹500)
- [ ] Verify category appears in dropdown

### 2. QR Generation
- [ ] Generate batch with Distributor category
- [ ] Verify QR codes have category assigned
- [ ] Check QR codes are in "available" status

### 3. Payment Flow
- [ ] Scan QR code
- [ ] Verify redirect to payment page
- [ ] Check payment page shows correct amount
- [ ] Test payment with PhonePe
- [ ] Verify payment callback works
- [ ] Check DistributorPayment record created

### 4. Activation Flow
- [ ] After payment, verify redirect to activation
- [ ] Complete phone verification
- [ ] Complete OTP verification
- [ ] Enter vehicle details
- [ ] Verify QR activated successfully

### 5. Post-Activation Usage
- [ ] Test message sending (should be free)
- [ ] Test call making (should be free)
- [ ] Verify no wallet deductions
- [ ] Check usage statistics update

### 6. Edge Cases
- [ ] Try activating without payment (should block)
- [ ] Try paying twice (should skip to activation)
- [ ] Test payment failure handling
- [ ] Test already activated QR (should redirect to access page)

## Key Differences from Other Categories

| Feature | Free | Prepaid | Distributor |
|---------|------|---------|-------------|
| Initial Payment | No | No | Yes (one-time) |
| Activation | Direct | Direct | After payment |
| Usage | Unlimited | Pay per use | Unlimited |
| Wallet Recharge | No | Yes | No |
| Recurring Cost | No | Yes | No |

## Security Considerations

1. **Payment Verification:** Always verify payment status with PhonePe before allowing activation
2. **One-Time Check:** Payment is checked only during activation, not on every access
3. **Status Tracking:** DistributorPayment status prevents duplicate payments
4. **Session Security:** No sensitive data stored in sessions

## Future Enhancements

1. **Bulk Distributor Activation:** Admin can activate multiple QR codes for distributors
2. **Payment Reports:** Track distributor payments and revenue
3. **Discount Codes:** Apply promo codes to activation fee
4. **Partial Payments:** Allow installment payments (if needed)
5. **Refund System:** Handle refund requests for failed activations

## Support & Troubleshooting

### Common Issues

**Issue:** Payment successful but activation blocked
**Solution:** Check DistributorPayment status in database, manually mark as completed if needed

**Issue:** Payment page not showing
**Solution:** Verify category type is 'distributor' and activation_fee is set

**Issue:** Unlimited usage not working
**Solution:** Check QRWallet.can_send_message() and can_make_call() methods include distributor logic

## Files Modified

1. `apps/accounts/recharge_models.py` - Added category type, fee field, DistributorPayment model
2. `apps/accounts/models.py` - Import DistributorPayment
3. `apps/accounts/wallet_views.py` - Added payment views
4. `apps/accounts/urls.py` - Added payment routes
5. `apps/gateways/qr_views.py` - Modified activation flow
6. `templates/accounts/distributor_payment.html` - New payment template

## Summary

The Distributor category successfully implements a pay-once-then-free model:
- ✅ One-time payment before activation
- ✅ Payment verification via PhonePe
- ✅ Normal activation flow after payment
- ✅ Unlimited free usage (like Free category)
- ✅ No wallet recharge needed
- ✅ Clean user experience
- ✅ Admin configurable activation fee

The implementation is complete and ready for testing!
