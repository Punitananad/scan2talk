# Commission Payment - Quick Reference

## Admin Access
**URL**: `/accounts/admin/commissions/`  
**Menu**: Admin Dashboard → 💵 Commissions

## Quick Actions

### Pay Distributors (Bulk)
1. Go to Commission Payments page
2. Select commissions using checkboxes
3. Click "Mark Selected as Paid"
4. Add payment notes (optional)
5. Click "Confirm Payment"

### Pay Single Distributor
1. Filter by distributor name
2. Select their unpaid commissions
3. Mark as paid with notes

### Undo Payment
1. Filter by "Paid" status
2. Find the commission
3. Click "Mark Unpaid"

## Filters

| Filter | Options |
|--------|---------|
| Distributor | All / Specific distributor |
| Status | Unpaid / Paid / All |
| Date Range | From date → To date |

## Summary View

Shows for each distributor:
- **Total Sales**: Number of QR activations
- **Total Earned**: All commissions (₹)
- **Paid**: Amount already paid (₹)
- **Pending**: Amount waiting to be paid (₹)
- **Today**: Today's earnings (₹)

## Commission Flow

```
User Pays ₹500
    ↓
Commission Earned (₹100)
    ↓
Shows in "Unpaid" list
    ↓
Admin marks as paid
    ↓
Shows in "Paid" list
```

## Payment Notes Examples
- "Bank transfer #123456"
- "UPI to 9876543210"
- "Cash payment - Jan 25"
- "Cheque #789012"

## Files
- **Backend**: `apps/accounts/admin_views.py`
- **Template**: `templates/admin/manage_commission_payments.html`
- **Model**: `apps/accounts/recharge_models.py` (DistributorPayment)

---

**Quick Tip**: Use date filters for weekly/monthly payment runs!
