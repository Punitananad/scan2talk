# Distributor System - Quick Reference

## 🎯 Where is Distributor Code Entered?

### ✅ TAG ORDER FORM (Payment Page)
**URL**: `/order-tag/`

**When**: Customer orders physical QR tag
**Field**: "Distributor Code (Optional)"
**Format**: 10-digit mobile number
**Result**: Commission earned on successful payment

### ❌ QR ACTIVATION FORM (NOT HERE!)
**URL**: `/gateways/activate/{qr_code}/`

**When**: Customer activates received QR tag
**Field**: NO distributor code field
**Result**: No commission tracking

---

## 💰 Commission Flow

```
Customer Orders Tag
    ↓
Enters Distributor Code (Optional)
    ↓
Completes Payment (Razorpay)
    ↓
Payment Successful
    ↓
✅ DISTRIBUTOR EARNS COMMISSION
    ↓
Order saved with distributor_code
    ↓
Distributor Dashboard updated
```

---

## 📊 Dashboard Display

### Distributor Dashboard
**Shows**: Only 2 columns
- Commission (₹ amount)
- Date (with time)

**Does NOT show**:
- ❌ User name
- ❌ User email
- ❌ Vehicle number
- ❌ Owner name

**Why**: User details only available AFTER activation, but commission earned on PAYMENT

---

## 🔑 Key Points

1. **Commission = Payment** (not activation)
2. **Distributor Code = Tag Order Form** (not activation form)
3. **Dashboard = Commission + Date** (no user details)
4. **Admin Sets**: Total QR + Commission per payment

---

## 📝 Forms Comparison

### Tag Order Form (`/order-tag/`)
```
✓ Name
✓ Phone
✓ Email
✓ Address
✓ City
✓ State
✓ PIN Code
✓ Quantity
✓ Distributor Code ← HERE!
```

### QR Activation Form (`/gateways/activate/`)
```
✓ Name
✓ Vehicle Type
✓ Vehicle Number
✓ Vehicle Model
✗ Distributor Code ← NOT HERE!
```

---

## 🎯 Quick Test

### Test Commission Tracking
1. Register distributor → Get verified by admin
2. Customer orders tag → Enters distributor code
3. Payment successful
4. Check distributor dashboard → Commission shows ✅

### Test Activation (No Distributor Code)
1. Customer scans QR
2. Enters phone → OTP verification
3. Enters vehicle details (NO distributor code field)
4. Activation complete ✅

---

## 🔍 Database Fields

### TagOrder Model
```python
distributor_code = CharField(max_length=15, blank=True)
# Stores distributor's mobile number
# Filled during tag order payment
```

### Gateway Model
```python
# NO distributor_code field
# Commission NOT tracked here
```

---

## 📞 URLs

### Customer URLs
- Order Tag: `/order-tag/`
- Payment: `/order-tag/payment/`
- Success: `/order-tag/success/`
- Activate QR: `/gateways/activate/{qr_code}/`

### Distributor URLs
- Register: `/accounts/distributor/register/`
- Login: `/accounts/distributor/login/`
- Dashboard: `/accounts/distributor/dashboard/`

### Admin URLs
- Manage Distributors: `/admin/manage-distributors/`
- Super Dashboard: `/admin/super-dashboard/`

---

## 💡 Common Questions

### Q: Where do customers enter distributor code?
**A**: During tag order (before payment), NOT during QR activation

### Q: When does distributor earn commission?
**A**: When customer's payment is successful (processing/shipped/delivered status)

### Q: What does distributor dashboard show?
**A**: Only Commission and Date (2 columns)

### Q: Can I see which customer used my code?
**A**: No, user details not shown (only available after activation)

### Q: How does admin set commission?
**A**: Admin panel → Manage Distributors → Edit Details → Set Total QR + Commission

---

## ✅ Checklist

### For Distributors
- [ ] Register at `/accounts/distributor/register/`
- [ ] Wait for admin verification
- [ ] Login with mobile + OTP
- [ ] Share your mobile number as distributor code
- [ ] Customers enter your code during tag order
- [ ] Check dashboard for commission

### For Admins
- [ ] Access `/admin/manage-distributors/`
- [ ] Verify pending distributors
- [ ] Set Total QR count
- [ ] Set Commission per payment
- [ ] Monitor distributor stats

### For Customers
- [ ] Visit `/order-tag/`
- [ ] Fill order form
- [ ] Enter distributor code (optional)
- [ ] Complete payment
- [ ] Receive QR tag
- [ ] Activate QR (no distributor code needed)

---

**Remember**: Commission on PAYMENT, not activation! 💰
