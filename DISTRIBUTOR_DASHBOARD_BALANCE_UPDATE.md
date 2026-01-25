# Distributor Dashboard - Balance & Payment Status Update

## Changes Made

Updated the distributor dashboard to show detailed balance information and payment status for each commission.

## New Features

### 1. Separate Balance Tracking
- **Pending Balance**: Amount earned but not yet paid by admin (yellow)
- **Paid Amount**: Amount already paid by admin (green)
- **Total Earned**: Sum of pending + paid

### 2. Updated Available QR Calculation
- **Before**: Available = Total - Activated
- **After**: Available = Total - Paid Commissions

**Logic**: Available QR only decreases when admin PAYS the commission, not when QR is activated.

### 3. Payment Status in Recent Commissions
Each commission now shows:
- Commission amount
- Date earned
- Payment status:
  - ✓ Paid (green badge) with payment date
  - ⏳ Pending (yellow badge) with "Awaiting payment"

## Dashboard Cards (5 Cards)

### Card 1: Total QR Codes
- Shows total QR assigned by admin
- Purple gradient background

### Card 2: Activated
- Shows number of QRs activated (completed payments)
- Green icon

### Card 3: Available
- Shows QRs available to distribute
- Calculation: Total - Paid commissions
- Shows "After X paid" subtitle
- Blue icon

### Card 4: Pending Balance (NEW)
- Shows amount waiting to be paid
- Shows number of unpaid commissions
- Yellow icon
- Example: "₹300" with "3 unpaid"

### Card 5: Paid Amount (NEW)
- Shows amount already paid by admin
- Shows number of paid commissions
- Green icon
- Example: "₹700" with "7 paid by admin"

## Example Scenario

**Distributor has:**
- Total QR: 10
- Activated: 8 (8 users paid activation fee)
- Commission per activation: ₹100

**Admin paid 5 commissions:**
- Paid Amount: ₹500 (5 × ₹100)
- Pending Balance: ₹300 (3 × ₹100)
- Available QR: 5 (10 - 5 paid)

**Dashboard shows:**
```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Total QR     │ Activated    │ Available    │ Pending      │ Paid Amount  │
│ 10           │ 8            │ 5            │ ₹300         │ ₹500         │
│ Assigned     │ Using code   │ After 5 paid │ 3 unpaid     │ 5 paid       │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

## Recent Commissions Table

Shows 3 columns:
1. **Commission**: Amount (₹100)
2. **Date Earned**: When user paid activation fee
3. **Payment Status**: 
   - ✓ Paid (with date admin paid)
   - ⏳ Pending (awaiting payment)

## Backend Changes

### Updated `distributor_dashboard()` in `apps/accounts/distributor_views.py`:

**New calculations:**
```python
# Separate paid and unpaid
paid_payments = completed_payments.filter(commission_paid=True)
unpaid_payments = completed_payments.filter(commission_paid=False)

paid_count = paid_payments.count()
unpaid_count = unpaid_payments.count()

# Calculate amounts
total_earned = completed_payments.aggregate(total=Sum('commission_amount'))['total'] or 0
paid_amount = paid_payments.aggregate(total=Sum('commission_amount'))['total'] or 0
pending_balance = unpaid_payments.aggregate(total=Sum('commission_amount'))['total'] or 0

# Available QR = Total - Paid (not activated)
available_qrs = total_qrs - paid_count
```

**New context variables:**
- `paid_qrs`: Number of commissions paid by admin
- `unpaid_qrs`: Number of commissions pending payment
- `total_earned`: Total amount earned (all time)
- `paid_amount`: Amount already paid by admin
- `pending_balance`: Amount waiting to be paid

## Files Modified

1. **`apps/accounts/distributor_views.py`**
   - Updated `distributor_dashboard()` function
   - Added separate paid/unpaid calculations
   - Changed available QR logic

2. **`templates/accounts/distributor_dashboard.html`**
   - Changed from 4 cards to 5 cards
   - Added "Pending Balance" card
   - Added "Paid Amount" card
   - Updated "Available" card subtitle
   - Added payment status column to table
   - Shows ✓ Paid or ⏳ Pending badges

## User Experience

### Before:
- Only showed "Total Revenue" (confusing)
- No payment status visibility
- Available QR decreased on activation

### After:
- Clear separation: Pending vs Paid
- Payment status for each commission
- Available QR decreases only when admin pays
- Distributor knows exactly what they're owed

## Benefits

✅ **Transparency**: Distributor sees exactly what's pending and what's paid  
✅ **Accurate Available Count**: Available QR reflects actual payment status  
✅ **Payment Tracking**: Each commission shows if it's been paid  
✅ **Better Planning**: Distributor knows how many QR they can still distribute  
✅ **Trust**: Clear visibility builds trust between admin and distributor

---

**Date**: January 25, 2026  
**Status**: ✅ Complete  
**Version**: 1.0
