# Admin Guide: Setting Up Distributors

## Quick Checklist

When a new distributor registers, admin MUST:

1. ✅ Verify distributor account
2. ✅ Set commission per activation
3. ✅ Set total QR codes assigned
4. ✅ Inform distributor of their ID (mobile number)

## Step-by-Step Process

### Step 1: Distributor Registers
- Distributor visits: `/accounts/distributor/register/`
- Enters: Name, Mobile, Email, Bank Details
- Verifies OTP
- Account created with `distributor_verified=False`

### Step 2: Admin Approves (Django Admin)
1. Go to Django Admin: `/admin/`
2. Navigate to: **Users** → Find the distributor
3. Edit the user:
   - ✅ Check `is_distributor`
   - ✅ Check `distributor_verified`
   - ✅ Set `distributor_commission_per_activation` (e.g., 100.00)
   - ✅ Set `distributor_total_qr` (e.g., 10)
4. Save

### Step 3: Inform Distributor
Send message to distributor:
```
Your distributor account has been approved!

Your Distributor ID: [MOBILE_NUMBER]
Commission per Activation: ₹[AMOUNT]
Total QR Codes Assigned: [COUNT]

Share your Distributor ID with customers when giving them QR tags.
```

## Important Fields

### distributor_commission_per_activation
- **Type**: Decimal
- **Example**: 100.00 (means ₹100 per activation)
- **Purpose**: How much distributor earns per successful payment
- **Default**: 0.00 ❌ (MUST be set by admin)

### distributor_total_qr
- **Type**: Integer
- **Example**: 10 (means 10 QR codes assigned)
- **Purpose**: Total QR codes distributor can distribute
- **Default**: 0 ❌ (MUST be set by admin)

### distributor_verified
- **Type**: Boolean
- **Purpose**: Controls if distributor can login and see dashboard
- **Default**: False (admin must set to True)

## How Distributors Earn Commission

### Flow
```
1. Distributor gives physical QR tag to customer
2. Customer scans QR → Payment page
3. Customer enters Distributor ID (mobile number)
4. Customer pays activation fee (e.g., ₹500)
5. ✅ Commission earned IMMEDIATELY (before activation)
6. Customer proceeds to activate QR
```

### Commission Calculation
```
Total Revenue = Completed Payments × Commission per Activation

Example:
- 5 customers paid using distributor ID
- Commission = ₹100 per activation
- Total Revenue = 5 × ₹100 = ₹500
```

## Distributor Dashboard

Distributors see:
- **Total QR Codes**: Assigned by admin
- **Activated**: Number of completed payments
- **Available**: Total - Activated
- **Total Revenue**: Activated × Commission
- **Recent Commissions**: List showing Commission and Date only

## Common Issues & Solutions

### Issue 1: Dashboard Shows ₹0 Revenue
**Cause**: Commission not set by admin  
**Solution**: Set `distributor_commission_per_activation` in Django Admin

### Issue 2: Dashboard Shows 0 Activations
**Cause**: Payments not linked to distributor  
**Solution**: Run `python auto_fix_distributor_payment.py`

### Issue 3: Distributor Can't Login
**Cause**: `distributor_verified=False`  
**Solution**: Set `distributor_verified=True` in Django Admin

### Issue 4: Available QR Shows 0
**Cause**: `distributor_total_qr` not set  
**Solution**: Set `distributor_total_qr` in Django Admin

## Admin Panel Access

### View All Distributors
```
URL: /admin/accounts/manage-distributors/
Shows:
- Distributor name
- Phone number
- Total QR assigned
- Activated count
- Total revenue
```

### Edit Distributor
```
URL: /admin/auth/user/[USER_ID]/change/
Fields to set:
- distributor_verified: True
- distributor_commission_per_activation: 100.00
- distributor_total_qr: 10
```

## Recommended Commission Rates

Based on activation fee of ₹500:

| Commission | Percentage | Distributor Earns | Platform Keeps |
|------------|------------|-------------------|----------------|
| ₹50        | 10%        | ₹50               | ₹450           |
| ₹100       | 20%        | ₹100              | ₹400           |
| ₹150       | 30%        | ₹150              | ₹350           |
| ₹200       | 40%        | ₹200              | ₹300           |

**Recommended**: ₹100 (20% commission)

## QR Code Assignment

### How to Assign QR Codes
1. Generate QR codes in batch
2. Set category to "Distributor"
3. Physically print and give to distributor
4. Set `distributor_total_qr` to match count given

### Tracking
- System automatically tracks which QR codes have payments
- Dashboard shows: Total - Activated = Available
- Example: 10 total, 3 activated = 7 available

## Payment Flow Details

### What Happens When Customer Pays
1. Customer enters Distributor ID (mobile number)
2. System finds distributor by phone
3. Creates `DistributorPayment` record:
   ```python
   DistributorPayment.objects.create(
       qr_code=qr,
       distributor=distributor_user,  # ← Linked here
       amount=500,
       status='pending'
   )
   ```
4. Payment successful → `status='completed'`, `paid_at=now()`
5. Commission earned ✅
6. Dashboard updates automatically

### What Distributor Sees
```
Recent Commissions:
┌─────────────┬──────────────────┐
│ Commission  │ Date             │
├─────────────┼──────────────────┤
│ ₹100        │ Jan 24, 2026     │
│             │ 6:03 PM          │
└─────────────┴──────────────────┘
```

## Security Notes

1. **Distributor ID = Mobile Number**: Easy to remember, secure
2. **OTP Verification**: Required for login and registration
3. **Admin Approval**: Distributors can't self-activate
4. **Payment Tracking**: All payments logged with timestamps
5. **No User Data**: Distributors don't see customer details

## Testing Checklist

After setting up a distributor, test:

- [ ] Distributor can login with mobile + OTP
- [ ] Dashboard shows correct Total QR count
- [ ] Dashboard shows correct Commission rate
- [ ] Make test payment with distributor ID
- [ ] Dashboard updates with new activation
- [ ] Revenue calculates correctly
- [ ] Recent commissions table shows entry

## Support

If distributor reports issues:
1. Check `distributor_verified=True`
2. Check `distributor_commission_per_activation > 0`
3. Check `distributor_total_qr > 0`
4. Run diagnostic: `python debug_distributor_commission.py`
5. Check payment links: Look for orphan payments

---

**Last Updated**: January 24, 2026  
**Version**: 1.0
