# 📍 Where to Find the Pricing Control Button

## Visual Guide

### Step 1: Login to Admin
```
Go to: /admin/
Login with your admin credentials
```

### Step 2: Go to Admin Dashboard
```
Click: "Admin Dashboard" or go to /accounts/admin/dashboard/
```

### Step 3: Find the Pricing Control Button
```
Look for the AMBER/GOLD colored button with 💲 icon
It's in the "Secondary Actions" row
First button on the left
```

## What It Looks Like

```
┌─────────────────────────────────────────────────────────────┐
│                     Admin Dashboard                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Big Blue Cards: QR Dashboard, Batch Management, etc.]     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Secondary Actions:                                          │
│                                                              │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │      💲      │  │    📂    │  │    💰    │  │   🏪    ││
│  │   Pricing    │  │Categories│  │QR Wallets│  │Distribu-││
│  │   Control    │  │          │  │          │  │  tors   ││
│  │ Tag & Dist.  │  │  Manage  │  │  Manage  │  │ Manage  ││
│  │    Fees      │  │  pricing │  │ balances │  │registra-││
│  │              │  │          │  │          │  │  tions  ││
│  └──────────────┘  └──────────┘  └──────────┘  └─────────┘│
│   ↑ THIS ONE!                                                │
│   AMBER/GOLD COLOR                                           │
└─────────────────────────────────────────────────────────────┘
```

## Button Details

### Visual Characteristics
- **Color**: Amber/Gold gradient (stands out from white buttons)
- **Icon**: 💲 (dollar sign)
- **Title**: "Pricing Control"
- **Subtitle**: "Tag & Distributor Fees"
- **Border**: Amber border (thicker than others)
- **Shadow**: Subtle shadow effect

### Location
- **Section**: Secondary Actions (below main cards)
- **Position**: First button (leftmost)
- **Grid**: 5 buttons in a row on desktop
- **Mobile**: Stacks vertically

## Alternative Access Methods

### Method 1: Direct URL
```
/admin/core/pricingsettings/
```

### Method 2: Django Admin
```
1. Go to /admin/
2. Look for "Core" section
3. Click "Pricing Settings"
```

### Method 3: Search
```
In Django admin, use search bar:
Type "pricing" → Click "Pricing Settings"
```

## What You'll See When You Click

```
┌─────────────────────────────────────────────────────────────┐
│  Change Pricing Settings                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Physical Tag Pricing                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Tag price: [  499.00  ] ₹                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  Set the price for physical QR tags sold to customers       │
│                                                              │
│  Distributor Pricing                                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Distributor activation fee: [  1.00  ] ₹              │ │
│  └────────────────────────────────────────────────────────┘ │
│  Set the one-time activation fee for distributor category   │
│                                                              │
│  [Save and continue editing]  [Save]  [Delete]              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Test

### Can You Find It?
1. ✅ Login to admin
2. ✅ Go to Admin Dashboard
3. ✅ Scroll down past the big blue cards
4. ✅ Look for AMBER/GOLD button with 💲
5. ✅ Click it!

### What to Do Next
1. Change "Distributor activation fee" to any value
2. Click "Save"
3. Check distributor payment page
4. Verify new price shows up ✅

## Troubleshooting

### Can't See the Button?
- **Check**: Are you logged in as staff/admin?
- **Check**: Are you on the Admin Dashboard page?
- **Check**: Scroll down - it's below the big cards
- **Try**: Refresh the page (Ctrl+F5)

### Button Not Working?
- **Check**: Server is running
- **Check**: No JavaScript errors in console
- **Try**: Clear browser cache

### Can't Access Pricing Settings?
- **Check**: You have staff permissions
- **Try**: Direct URL: `/admin/core/pricingsettings/`
- **Try**: Django admin: `/admin/` → Core → Pricing Settings

## Mobile View

On mobile devices:
```
┌──────────────────┐
│   Admin Dash     │
├──────────────────┤
│                  │
│  [Big Cards]     │
│  [Stack]         │
│  [Vertically]    │
│                  │
├──────────────────┤
│  ┌────────────┐  │
│  │     💲     │  │
│  │  Pricing   │  │
│  │  Control   │  │
│  └────────────┘  │
│  ↑ HERE!         │
│                  │
│  [Categories]    │
│  [QR Wallets]    │
│  [Distributors]  │
│  [Tag Orders]    │
└──────────────────┘
```

## Summary

**Location**: Admin Dashboard → Secondary Actions → First Button (Amber/Gold with 💲)

**Direct URL**: `/admin/core/pricingsettings/`

**Look For**: 
- Amber/Gold color (stands out)
- 💲 icon
- "Pricing Control" text
- "Tag & Distributor Fees" subtitle

**Can't Miss It**: It's the only amber/gold colored button in that section!

---

**Still can't find it?** Try the direct URL: `/admin/core/pricingsettings/`
