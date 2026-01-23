# Where to Find Distributor Management

## 🎯 Quick Answer

Go to your **Admin Dashboard** and click the **"Distributors"** card (🏪 icon).

## 📍 Step-by-Step

### Method 1: From Admin Dashboard (Recommended)

1. **Login as admin**
   - Go to your website
   - Login with admin credentials

2. **Go to Admin Dashboard**
   - URL: `/accounts/admin/dashboard/`
   - Or click "Admin Dashboard" in navigation

3. **Find the Distributors Card**
   - Look in the "Secondary Actions" section
   - It's a white card with 🏪 icon
   - Says "Distributors" with "Manage registrations" subtitle

4. **Click the Card**
   - Takes you to `/accounts/admin/distributors/`
   - Shows all distributor registrations

### Method 2: Direct URL

Just go to: **`/accounts/admin/distributors/`**

Example:
- Local: `http://localhost:8000/accounts/admin/distributors/`
- Production: `https://scan2talk.in/accounts/admin/distributors/`

## 🖼️ What You'll See

### Admin Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│                   Admin Dashboard                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │    📱    │  │    📦    │  │    ➕    │  │    👥    ││
│  │    QR    │  │  Batch   │  │ Generate │  │   All    ││
│  │Dashboard │  │Management│  │    QR    │  │  Users   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │   📂    │  │   💰    │  │   🏪    │  │   📦    │   │
│  │Categories│ │QR Wallets│ │Distribu-│ │Tag Orders│   │
│  │         │  │         │  │  tors   │  │         │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
│                                 ↑                        │
│                          CLICK HERE!                     │
└─────────────────────────────────────────────────────────┘
```

### Distributor Management Page

```
┌─────────────────────────────────────────────────────────┐
│              Distributor Management                      │
│  View and manage distributor registrations               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐     │
│  │  10  │  │  3   │  │  7   │  │  28  │  │  15  │     │
│  │Total │  │Pend- │  │Veri- │  │Total │  │Activ-│     │
│  │Dist. │  │ ing  │  │ fied │  │ QRs  │  │ated  │     │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Search: [____________]  Status: [All ▼]  [Filter] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Distributor │ Phone │ Status │ QRs │ Actions      │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ John Doe    │ 98765 │⏳Pend │ 0/0 │[Verify]      │ │
│  │ jane@ex.com │ 43210 │       │     │              │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Jane Smith  │ 98765 │✓Verif │ 5/10│[Reset][Revoke]│
│  │ john@ex.com │ 12345 │       │     │              │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🔍 What to Look For

### On Admin Dashboard:
- **Icon**: 🏪 (store/shop icon)
- **Title**: "Distributors"
- **Subtitle**: "Manage registrations"
- **Location**: Second row of cards
- **Color**: White card with gray border
- **Hover**: Border turns blue

### On Distributor Page:
- **Title**: "Distributor Management"
- **Statistics**: 5 cards showing counts
- **Table**: List of all distributors
- **Filters**: Search and status dropdown
- **Actions**: Verify, Reset Password, Revoke buttons

## 🎨 Visual Indicators

### Status Badges:
- **⏳ Pending**: Yellow badge - needs your action
- **✓ Verified**: Green badge - approved and active

### Action Buttons:
- **Green button**: "Verify & Assign Password" (pending only)
- **Blue button**: "Reset Password" (verified only)
- **Red button**: "Revoke" (verified only)

## 📱 Mobile View

On mobile devices:
1. Scroll down on admin dashboard
2. Look for "Distributors" card
3. Tap to open
4. Table scrolls horizontally
5. Actions stack vertically

## ⚡ Quick Access

### Bookmark These URLs:

**Admin Dashboard**:
```
http://localhost:8000/accounts/admin/dashboard/
```

**Distributor Management**:
```
http://localhost:8000/accounts/admin/distributors/
```

### Browser Bookmarks:
1. Open the page
2. Press `Ctrl+D` (Windows) or `Cmd+D` (Mac)
3. Save as "Distributor Management"

## 🔐 Access Requirements

You must be:
- ✅ Logged in
- ✅ Staff member (`is_staff=True`)
- ✅ Have admin permissions

If you see "Permission Denied":
1. Make sure you're logged in
2. Check if your account is staff
3. Contact super admin to grant permissions

## 🆘 Troubleshooting

### "Can't find the Distributors card"
- Scroll down on admin dashboard
- It's in the second row of cards
- Look for 🏪 icon
- Refresh the page

### "Page not found (404)"
- Check URL is correct
- Make sure you're logged in as admin
- Verify you have staff permissions
- Try going to admin dashboard first

### "Permission denied"
- You need staff/admin access
- Contact super admin
- Check your user permissions in Django admin

## 📞 Need Help?

1. **Read the guide**: `DISTRIBUTOR_ADMIN_GUIDE.md`
2. **Check URLs**: Make sure you're using correct path
3. **Verify access**: Confirm you're logged in as admin
4. **Clear cache**: Try refreshing the page
5. **Check console**: Look for JavaScript errors

## ✅ Checklist

Before looking for distributors:
- [ ] Logged in as admin
- [ ] On admin dashboard page
- [ ] Can see other admin cards (QR Dashboard, etc.)
- [ ] Have staff permissions
- [ ] Page fully loaded

## 🎉 That's It!

The distributor management is right there on your admin dashboard. Just click the **"Distributors"** card with the 🏪 icon!

**Direct link**: `/accounts/admin/distributors/`
