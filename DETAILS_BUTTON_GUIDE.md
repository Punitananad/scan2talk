# Details Button - Quick Guide

## What You'll See in Dashboard

### Before (Old Dashboard)
```
Actions Column:
View | Download | Delete | Activate
```

### After (New Dashboard)
```
Actions Column (for Activated QR):
Details | View | Download | Delete
       ↑
    NEW BUTTON (Purple)
```

## Click Flow

```
Dashboard
   ↓ (Click "Details" button)
Detail Page
   ↓ (Shows)
┌─────────────────────────────────────┐
│ QR Code Details                     │
├─────────────────────────────────────┤
│ QR Code: ZQ0VCCEZ                   │
│ Status: Activated                   │
│ Access Count: 6                     │
├─────────────────────────────────────┤
│ OWNER INFORMATION                   │
│ • Full Name: John Doe               │
│ • Phone: +91-9876543210             │
│ • Email: john@example.com           │
│ • User ID: 123e4567-...             │
│ • Account Created: Jan 5, 2026      │
│ • Phone Verified: ✓ Verified        │
├─────────────────────────────────────┤
│ VEHICLE INFORMATION                 │
│ • Vehicle Type: Car                 │
│ • Vehicle Number: DL-01-AB-1234     │
│ • Make & Model: Toyota Camry 2020   │
│ • Gateway Title: Car - DL-01-AB-1234│
├─────────────────────────────────────┤
│ USAGE STATISTICS                    │
│ • Total QR Scans: 6                 │
│ • Contact Requests: 2               │
│ • Last Contact: 2 hours ago         │
├─────────────────────────────────────┤
│ ACCESS URLS                         │
│ • Activation URL: [Copy]            │
│ • Public Access URL: [Copy]         │
└─────────────────────────────────────┘
```

## When Details Button Shows

| QR Status | Details Button |
|-----------|----------------|
| Available | ❌ No (not activated yet) |
| Reserved | ❌ No (not activated yet) |
| **Activated** | ✅ **YES** (shows button) |
| Expired | ❌ No |

## Quick Access

### From Dashboard:
1. Find your QR code row
2. Look at Actions column
3. Click purple "Details" button
4. See complete information

### Direct URL:
```
http://localhost:8000/gateways/qr/<QR-ID>/details/
```

Replace `<QR-ID>` with the UUID from the database.

## Information Sections

### 1. QR Code Info (Top Card)
- QR Code number
- Status badge
- Access count (big number)
- Batch number
- Created date
- Activated date
- Last accessed date

### 2. Owner Information (Blue Icon)
- Full name entered during activation
- Phone number used for OTP
- Email address
- User ID (UUID)
- Account creation date
- Phone verification status

### 3. Vehicle Information (Purple Icon)
- Vehicle type (Car, Bike, etc.)
- License plate / Vehicle number
- Make and model
- Gateway title

### 4. Usage Statistics (Green Icon)
- Total QR scans
- Contact requests received
- Last contact time

### 5. Access URLs (Orange Icon)
- Activation URL (for new users)
- Public access URL (for contacting owner)
- Copy buttons for easy sharing

## Color Coding

| Element | Color | Meaning |
|---------|-------|---------|
| Details Button | Purple | Primary action |
| Status: Activated | Blue | Active status |
| Access Count | Blue | Metric |
| Owner Section | Blue icon | User info |
| Vehicle Section | Purple icon | Vehicle info |
| Statistics Section | Green icon | Analytics |
| URLs Section | Orange icon | Links |

## Use Cases

### 1. Customer Support
**Scenario:** User calls saying they can't access their QR
**Solution:** 
- Search QR code in dashboard
- Click "Details"
- Verify their name and phone
- Check access count and last access
- Troubleshoot based on data

### 2. Verification
**Scenario:** Need to verify vehicle ownership
**Solution:**
- Find QR code
- Click "Details"
- Check owner name matches
- Verify vehicle number
- Confirm phone number

### 3. Analytics
**Scenario:** Want to see QR usage
**Solution:**
- Click "Details" on any activated QR
- View access count
- Check contact requests
- See last interaction time

### 4. URL Sharing
**Scenario:** Need to share QR access URL
**Solution:**
- Click "Details"
- Scroll to Access URLs
- Click "Copy" button
- Share URL

## Mobile Responsive

The detail page is fully responsive:
- Desktop: 2-column layout
- Tablet: 2-column layout
- Mobile: 1-column stacked layout

## Security

✅ Only staff members can access
✅ Requires admin login
✅ Protected routes
✅ No public access to user data

## Quick Tips

1. **Find activated QR quickly:** Filter by "Activated" status
2. **Copy URLs easily:** Use the copy buttons
3. **Check usage:** Look at access count and interactions
4. **Verify user:** Match name and phone number
5. **Back to dashboard:** Click "Back to Dashboard" button

## Summary

The Details button gives you **instant access** to:
- ✅ Who owns the QR
- ✅ What vehicle it's for
- ✅ How it's being used
- ✅ When it was last accessed

All in one clean, organized page!
