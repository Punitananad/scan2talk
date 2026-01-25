# Commission Payment Management System

## Overview
Admin can now manage distributor commission payments manually. The system tracks all commissions earned by distributors and allows admin to mark them as paid with payment notes.

## Features

### 1. Commission Tracking
- Automatic commission calculation when payment is completed
- Commission amount set based on distributor's commission rate
- Tracks payment status (Paid/Unpaid)
- Records who paid and when

### 2. Admin Dashboard
- View all distributor commissions (paid and unpaid)
- Filter by distributor, status, and date range
- Distributor summary showing:
  - Total sales
  - Total earned
  - Total paid
  - Pending payment
  - Today's earnings

### 3. Bulk Payment Processing
- Select multiple commissions using checkboxes
- Mark selected commissions as paid in one action
- Add payment notes (transaction ID, payment method, etc.)
- Undo payment if needed (mark as unpaid)

## Database Changes

### New Fields in `DistributorPayment` Model:

```python
commission_amount = DecimalField(default=0.00)
# Commission earned by distributor

commission_paid = BooleanField(default=False)
# Has the commission been paid to distributor?

commission_paid_at = DateTimeField(null=True, blank=True)
# When was the commission paid?

commission_paid_by = ForeignKey(User)
# Admin who marked commission as paid

payment_notes = TextField(blank=True)
# Notes about commission payment (transaction ID, etc.)
```

## How It Works

### Commission Flow:

```
1. User scans QR code with distributor ID
2. User pays ₹500 activation fee
3. DistributorPayment created with:
   - distributor link
   - amount = ₹500
   - status = 'pending'
   - commission_amount = 0

4. Payment successful (Razorpay callback)
   - status = 'completed'
   - paid_at = now()
   - commission_amount = distributor.distributor_commission_per_activation
   - commission_paid = False (unpaid)

5. Admin views commission payments page
   - Sees unpaid commission
   - Selects commission(s)
   - Adds payment notes
   - Marks as paid

6. Commission marked as paid:
   - commission_paid = True
   - commission_paid_at = now()
   - commission_paid_by = admin user
   - payment_notes = "Bank transfer #123456"
```

## Admin Interface

### Access
- URL: `/accounts/admin/commissions/`
- Menu: Admin Dashboard → Commissions

### Summary Cards
1. **Total Commissions**: All commissions earned
2. **Paid**: Total amount paid to distributors
3. **Pending Payment**: Amount waiting to be paid

### Distributor Summary Table
Shows for each distributor:
- Name and email
- Total sales count
- Total earned (all time)
- Total paid
- Pending payment
- Today's earnings

### Filters
- **Distributor**: Filter by specific distributor
- **Status**: Unpaid / Paid / All
- **Date Range**: From date to date

### Commission Payments Table
Columns:
- Checkbox (for unpaid only)
- Date (when payment was received)
- Distributor (name and phone)
- QR Code
- Commission amount
- Status (Paid/Unpaid badge)
- Paid by (admin name and date)
- Actions (Mark Unpaid button for paid commissions)

### Bulk Actions
1. Select commissions using checkboxes
2. Click "Mark Selected as Paid"
3. Enter payment notes (optional)
4. Confirm payment
5. Commissions marked as paid

### Undo Payment
- Click "Mark Unpaid" on any paid commission
- Resets commission to unpaid status
- Clears payment date and admin info

## API Endpoints

### View Commission Payments
```
GET /accounts/admin/commissions/
```
Query parameters:
- `distributor`: Filter by distributor ID
- `status`: unpaid | paid | all
- `date_from`: YYYY-MM-DD
- `date_to`: YYYY-MM-DD

### Mark Commissions as Paid
```
POST /accounts/admin/commissions/mark-paid/
```
Body:
- `payment_ids[]`: Array of payment IDs
- `payment_notes`: Optional notes

Response:
```json
{
  "success": true,
  "message": "Marked 3 commission(s) as paid (₹300)",
  "count": 3,
  "amount": 300.00
}
```

### Mark Commission as Unpaid
```
POST /accounts/admin/commissions/<payment_id>/mark-unpaid/
```

## Distributor Dashboard Updates

Distributors can see:
- Total QR assigned
- Activated QRs (completed payments)
- Available QRs
- Commission per activation
- Total revenue (earned)
- Recent payments with commission and date

**Note**: Dashboard shows "Total Revenue" which is total earned, NOT total paid. This is the amount distributor has earned, regardless of payment status.

## Use Cases

### Use Case 1: Weekly Payment Run
1. Admin goes to Commission Payments page
2. Filters by "Unpaid" status
3. Filters date range (last 7 days)
4. Selects all commissions
5. Adds note: "Bank transfer - Week 4 Jan 2026"
6. Marks as paid
7. All selected commissions updated

### Use Case 2: Individual Distributor Payment
1. Admin filters by specific distributor
2. Reviews their unpaid commissions
3. Selects commissions to pay
4. Adds note: "UPI payment to 9876543210"
5. Marks as paid

### Use Case 3: Payment Correction
1. Admin realizes payment was marked by mistake
2. Finds the commission in "Paid" filter
3. Clicks "Mark Unpaid"
4. Commission returns to unpaid status
5. Can be paid again later

### Use Case 4: Monthly Report
1. Admin filters by date range (last month)
2. Filters by "Paid" status
3. Reviews all payments made
4. Exports data for accounting

## Files Modified

### Backend:
1. `apps/accounts/recharge_models.py`
   - Added commission payment tracking fields to DistributorPayment

2. `apps/accounts/admin_views.py`
   - Added `manage_commission_payments()` view
   - Added `mark_commissions_paid()` API
   - Added `mark_commission_unpaid()` API

3. `apps/accounts/wallet_views.py`
   - Updated `distributor_payment_success()` to set commission_amount

4. `apps/accounts/urls.py`
   - Added commission payment routes

### Frontend:
5. `templates/admin/manage_commission_payments.html`
   - Complete commission payment management interface

6. `templates/admin/super_dashboard.html`
   - Added "Commissions" link

### Database:
7. `apps/accounts/migrations/0009_add_commission_payment_tracking.py`
   - Migration for new fields

## Testing

### Test Scenario 1: New Payment
```bash
# 1. Create distributor payment (via QR activation)
# 2. Check commission_amount is set
# 3. Verify commission_paid = False
# 4. Go to admin commission page
# 5. Verify payment appears in unpaid list
```

### Test Scenario 2: Mark as Paid
```bash
# 1. Select unpaid commission
# 2. Add payment notes
# 3. Mark as paid
# 4. Verify commission_paid = True
# 5. Verify commission_paid_at is set
# 6. Verify commission_paid_by is admin user
```

### Test Scenario 3: Distributor Summary
```bash
# 1. Create multiple payments for distributor
# 2. Mark some as paid
# 3. Check distributor summary shows:
#    - Total earned (all commissions)
#    - Total paid (paid commissions)
#    - Total unpaid (unpaid commissions)
```

## Security

- Only staff members can access commission payment pages
- CSRF protection on all POST requests
- Payment IDs validated before updating
- Only unpaid commissions can be marked as paid via bulk action
- Audit trail: tracks who paid and when

## Future Enhancements

1. **Auto-payment Integration**
   - Connect to bank API for automatic transfers
   - Generate payment files for bulk transfers

2. **Email Notifications**
   - Notify distributors when commission is paid
   - Send payment receipt

3. **Export Functionality**
   - Export commission data to CSV/Excel
   - Generate payment reports

4. **Payment Scheduling**
   - Schedule automatic payment runs
   - Set payment frequency (weekly/monthly)

5. **Payment History**
   - Detailed payment history per distributor
   - Track payment methods used

## Troubleshooting

### Commission amount is 0
- Check if distributor has `distributor_commission_per_activation` set
- Admin must set this in distributor management page

### Commission not showing in list
- Check if payment status is 'completed'
- Check if distributor is linked to payment
- Verify payment has `paid_at` timestamp

### Cannot mark as paid
- Ensure payment is not already paid
- Check if user has staff permissions
- Verify CSRF token is valid

---

**Date**: January 25, 2026
**Status**: ✅ Complete
**Version**: 1.0
