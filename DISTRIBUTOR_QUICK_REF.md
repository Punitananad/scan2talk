# Distributor Category - Quick Reference Card

## 🎯 One-Line Summary
**Pay once → Activate → Use forever (free)**

## 📋 Quick Setup (3 Steps)

```bash
# 1. Migrate
python manage.py makemigrations && python manage.py migrate

# 2. Setup Category
python setup_distributor_category.py

# 3. Test
python test_distributor_category.py
```

## 🔄 User Flow

```
Scan QR → Pay ₹X → Phone → OTP → Vehicle → Activated → Use Forever
```

## 🔗 Key URLs

| Purpose | URL |
|---------|-----|
| Payment | `/accounts/distributor-payment/<QR_CODE>/` |
| Callback | `/accounts/distributor-payment-callback/<QR_CODE>/` |
| Activation | `/gateways/activate/<QR_CODE>/` |

## 💾 Database

### New Model: DistributorPayment
```python
qr_code (OneToOne)
amount
order_id (unique)
status (pending/completed/failed)
phone
paid_at
```

### Updated Model: RechargeCategory
```python
category_type = 'distributor'  # NEW
distributor_activation_fee  # NEW field
```

## 🎨 Category Settings

| Field | Value |
|-------|-------|
| Name | Distributor |
| Type | distributor |
| Activation Fee | ₹500 (configurable) |
| Message Cost | ₹0 |
| Call Cost | ₹0 |
| Free Limits | 0 (unlimited) |

## 🔍 Key Logic

### Payment Check (in activate_qr_code)
```python
if qr.category.category_type == 'distributor':
    payment = DistributorPayment.objects.get(qr_code=qr)
    if payment.status != 'completed':
        redirect to payment page
```

### Wallet Logic (unlimited usage)
```python
# can_send_message()
if category_type == 'distributor':
    return True, "Unlimited"

# deduct_message_credit()
if category_type == 'distributor':
    # No deduction, just count
    total_messages_sent += 1
```

## 🧪 Quick Test

```bash
# Create category
python setup_distributor_category.py

# Run tests
python test_distributor_category.py

# Manual test
# 1. Generate QR batch with Distributor category
# 2. Visit /gateways/activate/[QR_CODE]/
# 3. Should redirect to payment
# 4. Complete payment
# 5. Complete activation
# 6. Test unlimited usage
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Payment page not showing | Check category type = 'distributor' |
| Can activate without payment | Check payment verification in views |
| Wallet deducting credits | Check wallet methods include distributor |
| Payment not completing | Check PhonePe callback |

## 📊 Admin Quick Actions

### View Payments
Admin → Distributor Payments

### Create Category
Admin → Categories → Add → Type: Distributor

### Generate QR Batch
Generate QR → Select "Distributor" category

### Manual Payment Fix
Admin → Distributor Payments → Select → Mark as completed

## 🔐 Security Checks

✅ Payment verified before activation
✅ PhonePe callback validates status
✅ One-time payment per QR
✅ Cannot bypass payment

## 📈 Key Metrics

- Total distributor payments
- Payment success rate
- Average activation time
- Revenue from distributor category

## 💡 Use Cases

✅ **Good For:**
- Distributor sales
- Bulk pre-activation
- Fixed-cost model
- Corporate deployments

❌ **Not For:**
- Pay-per-use (use Prepaid)
- Free trials (use Trial)
- Completely free (use Free)

## 🎯 Success Indicators

✅ Payment page loads
✅ Payment processes
✅ Activation works
✅ Usage is unlimited
✅ No wallet deductions

## 📞 Quick Support

### User Issue
1. Check payment status in admin
2. Verify QR category
3. Check activation status
4. Review logs

### Payment Failed
1. Check PhonePe status
2. Retry payment
3. Manual completion if needed

### Activation Blocked
1. Verify payment completed
2. Check session
3. Clear cache
4. Retry activation

## 📁 Key Files

| File | Purpose |
|------|---------|
| `apps/accounts/recharge_models.py` | Models |
| `apps/accounts/wallet_views.py` | Payment views |
| `apps/gateways/qr_views.py` | Activation flow |
| `templates/accounts/distributor_payment.html` | Payment page |
| `apps/accounts/admin.py` | Admin interface |

## 🚀 Deployment

```bash
# 1. Pull code
git pull origin main

# 2. Migrate
python manage.py migrate

# 3. Restart
sudo systemctl restart gunicorn

# 4. Verify
curl https://yourdomain.com/accounts/distributor-payment/TEST123/
```

## 📚 Documentation

- **Full Guide:** `DISTRIBUTOR_CATEGORY_IMPLEMENTATION.md`
- **Quick Start:** `DISTRIBUTOR_CATEGORY_QUICK_START.md`
- **Summary:** `DISTRIBUTOR_CATEGORY_SUMMARY.md`
- **Checklist:** `DISTRIBUTOR_CATEGORY_CHECKLIST.md`
- **This Card:** `DISTRIBUTOR_QUICK_REF.md`

## ✅ Status

**Implementation:** ✅ Complete
**Testing:** ✅ Ready
**Documentation:** ✅ Complete
**Production:** ✅ Ready

---

**Need Help?** Check the full documentation or run the test script!
