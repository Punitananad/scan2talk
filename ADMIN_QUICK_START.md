# 🚀 Admin Quick Start Guide

## Getting Started (5 Minutes)

### Step 1: Login as Admin
```
1. Go to your site
2. Login with admin credentials
3. You should see "Admin" dropdown in navigation
```

### Step 2: Access Super Dashboard
```
Click: Admin → Super Dashboard
URL: /accounts/admin/dashboard/
```

You'll see:
- 📊 Complete system statistics
- 💰 Revenue breakdown
- 👥 User counts
- 📱 QR code stats
- ⚠️ Alerts and warnings

### Step 3: Create Categories (Optional)
```
Click: Admin → Categories
URL: /accounts/admin/categories/
```

**Quick Create**:
1. Click "Create Category"
2. Fill in:
   - Name: "Premium"
   - Type: "Prepaid"
   - Message Cost: ₹1.50
   - Call Cost: ₹1.00
3. Click "Save"

### Step 4: Create Plans
```
Click: Admin → Plans
URL: /accounts/admin/plans/
```

**Quick Create**:
1. Click "Create Plan"
2. Fill in:
   - Name: "Starter"
   - Amount: ₹99
   - Messages: 50
   - Minutes: 30
   - Validity: 30 days
3. Click "Save"

### Step 5: Manage QR Wallets
```
Click: Admin → QR Wallets
URL: /accounts/admin/qr-wallets/
```

**Quick Actions**:
- 💰 Add Credits - Click money icon
- 📂 Assign Category - Click folder icon
- 🚫 Suspend - Click stop icon

## Common Tasks

### Add Credits to QR Wallet
```
1. Go to QR Wallets
2. Find the QR code
3. Click 💰 icon
4. Enter:
   - Amount: ₹100
   - Messages: 50
   - Minutes: 30
5. Click "Add Credits"
```

### Assign Category to QR
```
1. Go to QR Wallets
2. Find the QR code
3. Click 📂 icon
4. Select category
5. Click "Assign"
```

### Suspend a Wallet
```
1. Go to QR Wallets
2. Find the QR code
3. Click 🚫 icon
4. Enter reason
5. Click "Suspend"
```

### View All Users
```
Click: Admin → Users
URL: /accounts/admin/users/
```

## Navigation Menu

When logged in as admin, you'll see:

```
Dashboard  Gateways  Wallet  Admin ▼
                              ├─ 🎛️ Super Dashboard
                              ├─ 📱 QR Dashboard
                              ├─ 📂 Categories
                              ├─ 💳 Plans
                              ├─ 👛 QR Wallets
                              ├─ 👥 Users
                              └─ 📋 Registrations
```

## Quick Reference

### URLs
```
Super Dashboard:    /accounts/admin/dashboard/
Categories:         /accounts/admin/categories/
Plans:              /accounts/admin/plans/
QR Wallets:         /accounts/admin/qr-wallets/
Users:              /accounts/admin/users/
QR Dashboard:       /gateways/q/dashboard/
Registrations:      /gateways/registrations/
```

### Category Types
```
🆓 Free      - Unlimited usage
🎁 Trial     - Limited free, then paid
💳 Prepaid   - Recharge before use
📱 Postpaid  - Use now, bill later
```

### Wallet Actions
```
💰 Add Credits
📂 Assign Category
🚫 Suspend
✅ Unsuspend
```

## Tips

1. **Set Default Category**: Mark one category as default for new QRs
2. **Monitor Low Balance**: Check dashboard for low balance alerts
3. **Track Revenue**: View revenue breakdown by day/week/month
4. **Bulk Operations**: Use filters to find specific QRs
5. **Transaction History**: Every action is logged

## Troubleshooting

### Can't see Admin menu?
- Make sure you're logged in as staff user
- Check: user.is_staff = True

### QR has no wallet?
- Wallets are auto-created when QR is generated
- If missing, contact developer

### Can't add credits?
- Make sure wallet is not suspended
- Check if QR is activated

## Support

For issues or questions:
1. Check COMPLETE_ADVANCED_SYSTEM.md
2. Check ADVANCED_SYSTEM_IMPLEMENTATION.md
3. Contact system administrator

---

**Quick Start Complete!** 🎉

You're now ready to manage your QR wallet system like a pro!
