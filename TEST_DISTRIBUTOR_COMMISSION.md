# Testing Distributor Commission System

## ✅ System is Running
Server started at: http://127.0.0.1:8000/

---

## 🧪 Test Flow

### Step 1: Create/Verify Distributor Account

#### Option A: Register New Distributor
1. Go to: http://127.0.0.1:8000/accounts/distributor/register/
2. Fill in details:
   - Full Name: Test Distributor
   - Mobile: 9876543210
   - Email: dist@test.com
   - Bank details (required)
3. Receive OTP → Verify
4. Account created (pending approval)

#### Option B: Login Existing Distributor
1. Go to: http://127.0.0.1:8000/accounts/distributor/login/
2. Enter mobile number
3. Receive OTP → Verify
4. Access dashboard

---

### Step 2: Admin Verification (Required for New Distributors)

1. Login as admin: http://127.0.0.1:8000/admin/
2. Go to: Super Dashboard → Manage Distributors
3. Find pending distributor
4. Click "Edit Details"
5. Set:
   - Total QR: 100
   - Commission per activation: 50
6. Click "Verify & Set Password"
7. Enter password (min 6 chars)
8. Distributor is now verified ✅

---

### Step 3: Customer Orders Tag with Distributor Code

1. Go to: http://127.0.0.1:8000/order-tag/
2. Fill order form:
   - Name: Test Customer
   - Phone: 9999999999
   - Email: customer@test.com
   - Address: Test Address
   - City: Delhi
   - State: Delhi
   - PIN: 110001
   - Quantity: 1
   - **Distributor Code: 9876543210** ← IMPORTANT
3. Click "Proceed to Payment"
4. Complete payment (Razorpay)
5. Payment successful ✅

---

### Step 4: Verify Commission in Distributor Dashboard

1. Login as distributor: http://127.0.0.1:8000/accounts/distributor/login/
2. View dashboard
3. Check:
   - Total QR: 100
   - Activated: 1 (represents successful payment)
   - Available: 99
   - Total Revenue: ₹50
4. See "Recent Commissions" table:
   - Commission: ₹50
   - Date: Jan 24, 2026 [time]

---

### Step 5: Verify in Admin Panel

1. Login as admin
2. Go to: Manage Distributors
3. Find distributor (9876543210)
4. Check stats:
   - Total QR: 100
   - Activated: 1
   - Available: 99
   - Revenue: ₹50

---

## 🔍 What to Check

### ✅ Distributor Dashboard Should Show:
- [x] Only 2 columns: Commission + Date
- [x] NO user details (car number, owner name)
- [x] Commission amount matches admin setting
- [x] Date/time of payment
- [x] Total revenue calculated correctly

### ✅ Admin Panel Should Show:
- [x] Payment count (not activation count)
- [x] Accurate revenue calculation
- [x] Distributor phone number
- [x] Edit Details button working

### ✅ Tag Order Form Should Have:
- [x] Distributor Code field (optional)
- [x] 10-digit validation
- [x] Help text explaining it's distributor's mobile

---

## 🐛 Troubleshooting

### Issue: Distributor code not saving
**Check**: 
- Form has `name="distributor_code"`
- Backend captures it in `order_data`
- Database field exists (migration applied)

### Issue: Commission not showing
**Check**:
- Payment status is 'processing', 'shipped', or 'delivered'
- Distributor code matches exactly (10 digits)
- Query filters correct in `distributor_views.py`

### Issue: Dashboard shows 4 columns
**Check**:
- Template updated to show only Commission + Date
- Browser cache cleared
- Server restarted

---

## 📊 Expected Results

### After 1 Successful Payment:
```
Distributor Dashboard:
├── Total QR: 100
├── Activated: 1
├── Available: 99
├── Total Revenue: ₹50
└── Recent Commissions:
    └── ₹50 | Jan 24, 2026 3:45 PM
```

### After 3 Successful Payments:
```
Distributor Dashboard:
├── Total QR: 100
├── Activated: 3
├── Available: 97
├── Total Revenue: ₹150
└── Recent Commissions:
    ├── ₹50 | Jan 24, 2026 4:30 PM
    ├── ₹50 | Jan 24, 2026 3:45 PM
    └── ₹50 | Jan 24, 2026 2:15 PM
```

---

## 🎯 Key Points to Remember

1. **Commission earned on PAYMENT**, not activation
2. **Distributor code entered during TAG ORDER**, not QR activation
3. **Dashboard shows only Commission + Date** (no user details)
4. **Payment must be successful** (processing/shipped/delivered)
5. **Distributor code is optional** (customer can skip it)

---

## 📝 Console Logs to Watch

When payment is successful with distributor code:
```
============================================================
💰 DISTRIBUTOR COMMISSION EARNED
   Distributor Code: 9876543210
   Order ID: TAG12345678
   Amount: ₹299
   Payment Status: SUCCESS
============================================================
```

---

## 🚀 Quick Test Commands

```bash
# Check if migration applied
python manage.py showmigrations core

# Check TagOrder model
python manage.py shell
>>> from apps.core.models import TagOrder
>>> TagOrder.objects.filter(distributor_code__isnull=False)

# Check distributor stats
>>> from apps.accounts.models import User
>>> dist = User.objects.get(is_distributor=True, distributor_verified=True)
>>> dist.get_decrypted_phone()
>>> TagOrder.objects.filter(distributor_code=dist.get_decrypted_phone()).count()
```

---

**Ready to Test!** 🎉

Server: http://127.0.0.1:8000/
Admin: http://127.0.0.1:8000/admin/
Order Tag: http://127.0.0.1:8000/order-tag/
Distributor Login: http://127.0.0.1:8000/accounts/distributor/login/
