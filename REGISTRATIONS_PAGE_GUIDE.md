# Registrations Page - Admin Guide

## Overview
A dedicated page showing **only activated QR codes** with complete registration details and the ability to deregister them.

## Access

### From QR Dashboard
```
http://localhost:8000/gateways/qr/dashboard/
↓ Click "📋 View Registrations" button
http://localhost:8000/gateways/qr/registrations/
```

### Direct URL
```
http://localhost:8000/gateways/qr/registrations/
```

## What You See

### Statistics (Top Cards)
```
┌─────────────────────────────────────────────────┐
│  Total Registrations  │  Total QR Scans  │  Total Contact Requests  │
│         2             │        12        │           5              │
└─────────────────────────────────────────────────┘
```

### Registrations Table
Shows all activated QR codes with:

| Column | Description | Example |
|--------|-------------|---------|
| **QR Code** | Unique QR identifier | ZQ0VCCEZ |
| **Owner Name** | Name entered during activation | John Doe |
| **Phone Number** | User's phone number | +91-9876543210 |
| **Vehicle Number** | License plate | DL-01-AB-1234 |
| **Vehicle Type** | Type of vehicle | Car |
| **Scans** | Total QR scans | 6 |
| **Contacts** | Contact requests received | 2 |
| **Activated** | Activation date/time | 2026-01-05 12:30 |
| **Actions** | View Details / Deregister | Buttons |

## Features

### 1. Search Functionality
Search across multiple fields:
- QR code
- Vehicle number
- Owner name
- Phone number

**Example:**
```
Search: "DL-01" → Finds all vehicles with DL-01 in number
Search: "John" → Finds all registrations by John
Search: "9876" → Finds registrations with this phone
```

### 2. View Details
Click **"View Details"** to see:
- Complete owner information
- Full vehicle details
- Usage statistics
- Access URLs
- All activation data

### 3. Deregister
Click **"Deregister"** to:
- Mark gateway as inactive
- Change QR status back to "Available"
- Free up vehicle number for reuse
- Allow QR to be activated again

## Deregister Process

### Step 1: Click Deregister
```
Click "Deregister" button on any registration
```

### Step 2: Confirmation Dialog
```
┌─────────────────────────────────────────────┐
│ Are you sure you want to deregister?       │
│                                             │
│ QR Code: ZQ0VCCEZ                          │
│ Vehicle: DL-01-AB-1234                     │
│                                             │
│ This will:                                  │
│ • Mark the gateway as inactive             │
│ • Make the QR code available for reuse     │
│ • Free up the vehicle number               │
│                                             │
│ [Cancel]  [OK]                             │
└─────────────────────────────────────────────┘
```

### Step 3: What Happens
```
✓ Gateway.is_active = False
✓ QR.status = 'available'
✓ QR.owner = None
✓ QR.gateway = None
✓ QR.activated_at = None
✓ Vehicle number freed up
```

### Step 4: Result
```
✓ Success message shown
✓ Registration removed from list
✓ QR code available in dashboard
✓ Vehicle number can be used again
```

## Use Cases

### 1. User Requests Removal
```
User: "Please remove my registration"
Admin: Goes to Registrations page
Admin: Searches for user's vehicle number
Admin: Clicks "Deregister"
Result: Registration removed
```

### 2. Vehicle Sold
```
Scenario: User sold their vehicle
Admin: Deregisters old owner's QR
New Owner: Can now register with same vehicle number
Result: Smooth ownership transfer
```

### 3. Duplicate Registration
```
Problem: Same vehicle registered twice (before validation)
Admin: Finds duplicate in Registrations page
Admin: Deregisters the incorrect one
Result: Only one valid registration remains
```

### 4. Testing Cleanup
```
Scenario: Test registrations need cleanup
Admin: Goes to Registrations page
Admin: Identifies test entries
Admin: Deregisters all test QRs
Result: Clean production data
```

## Differences from QR Dashboard

### QR Dashboard
- Shows **all** QR codes (available, activated, expired, etc.)
- Focus: QR code management
- Actions: Generate, download, delete QR codes
- View: QR-centric

### Registrations Page
- Shows **only activated** QR codes
- Focus: User registrations
- Actions: View details, deregister
- View: Registration-centric

## Data Preserved

When you deregister, these are **preserved**:
- ✅ Access count history
- ✅ Interaction count
- ✅ Last accessed date
- ✅ QR code image
- ✅ Batch information
- ✅ Creation date

When you deregister, these are **cleared**:
- ❌ Owner link
- ❌ Gateway link
- ❌ Activated date
- ❌ Active status

## Button Location

### In QR Dashboard Header
```
┌─────────────────────────────────────────────────────────┐
│ QR Code Dashboard                                       │
│ Manage all pre-generated QR codes                      │
│                                                         │
│ [📋 View Registrations] [Generate New] [🗑️ Delete All] │
└─────────────────────────────────────────────────────────┘
```

The purple **"📋 View Registrations"** button is prominently placed.

## Statistics Explained

### Total Registrations
- Count of all activated QR codes
- Shows how many vehicles are registered

### Total QR Scans
- Sum of all access_count values
- Shows total engagement across all QRs

### Total Contact Requests
- Sum of all total_interactions values
- Shows how many times people contacted owners

## Search Examples

### By QR Code
```
Search: "ZQ0V"
Result: Shows QR code ZQ0VCCEZ
```

### By Vehicle Number
```
Search: "HR12"
Result: Shows all vehicles with HR12 in number
```

### By Owner Name
```
Search: "punit"
Result: Shows all registrations by punit
```

### By Phone Number
```
Search: "9876"
Result: Shows registrations with this phone
```

## Security

- ✅ Only staff members can access
- ✅ Requires admin login
- ✅ Protected by `@staff_member_required`
- ✅ Confirmation required for deregister
- ✅ All actions logged

## Quick Actions

### View All Registrations
```
Dashboard → View Registrations button
```

### Search Specific Vehicle
```
Registrations page → Enter vehicle number → Search
```

### Deregister QR
```
Find registration → Click Deregister → Confirm
```

### View Full Details
```
Find registration → Click View Details
```

### Go Back to Dashboard
```
Click "← Back to Dashboard" button
```

## Summary

The Registrations page provides:

✅ **Focused View** - Only activated QR codes
✅ **Complete Information** - All registration details
✅ **Search Capability** - Find any registration quickly
✅ **Deregister Function** - Remove registrations when needed
✅ **Statistics** - Overview of all registrations
✅ **Clean Interface** - Easy to use and understand

Perfect for managing user registrations and handling support requests!
