# Distributor Admin Management Guide

## Overview

You can now view and manage all distributor registrations from the admin dashboard.

## How to Access

### Option 1: From Admin Dashboard
1. Go to `/accounts/admin/dashboard/`
2. Click on the **"Distributors"** card (🏪 icon)

### Option 2: Direct URL
Go to: `/accounts/admin/distributors/`

## What You'll See

### Statistics Cards
- **Total Distributors**: All registered distributors
- **Pending Verification**: Waiting for admin approval
- **Verified**: Approved and active distributors
- **Total QR Codes**: QR codes assigned to distributors
- **Activated QRs**: QR codes that have been activated

### Distributor Table

Each row shows:
- **Distributor Info**: Name, email, avatar
- **Phone**: Mobile number used for registration
- **Status**: 
  - ⏳ Pending (yellow badge) - Needs verification
  - ✓ Verified (green badge) - Approved and active
- **QR Codes**: Activated / Total count
- **Payments**: Number of successful payments
- **Revenue**: Total revenue from this distributor
- **Registered**: When they registered
- **Actions**: Buttons to manage the distributor

## Actions You Can Take

### 1. Verify Distributor (Pending Only)

For distributors with "⏳ Pending" status:

1. Click **"Verify & Assign Password"** button
2. Enter a secure password (minimum 6 characters)
3. Click **"Verify & Assign"**

**What happens:**
- Distributor status changes to "Verified"
- Password is assigned
- Distributor can now login at `/accounts/distributor/login/`
- They use: Mobile number + Password (no OTP needed)

**Example passwords:**
- `Dist@2026`
- `Secure123`
- `MyPass@456`

### 2. Reset Password (Verified Only)

For verified distributors:

1. Click **"Reset Password"** button
2. Enter new password (minimum 6 characters)
3. Click **"Reset Password"**

**Use this when:**
- Distributor forgot their password
- Security concerns
- Distributor requests password change

### 3. Revoke Distributor Status

For verified distributors:

1. Click **"Revoke"** button
2. Confirm the action

**What happens:**
- `is_distributor` set to `False`
- `distributor_verified` set to `False`
- They lose access to distributor dashboard
- Their QR codes remain but they can't login as distributor

**Use this when:**
- Distributor violated terms
- Account needs to be disabled
- Business relationship ended

## Filters

### Status Filter
- **All Status**: Show everyone
- **Pending**: Only unverified distributors
- **Verified**: Only approved distributors

### Search
Search by:
- Email address
- First name
- Last name

## Workflow Example

### Scenario: New Distributor Registration

1. **User registers** (from website):
   - Goes to profile
   - Clicks "Become a Distributor"
   - Enters phone number
   - Verifies OTP
   - Status: Pending

2. **Admin gets notified**:
   - Check admin dashboard
   - Click "Distributors"
   - See new entry with "⏳ Pending" badge

3. **Admin verifies**:
   - Click "Verify & Assign Password"
   - Enter password: `Dist@2026`
   - Click "Verify & Assign"
   - Status changes to "✓ Verified"

4. **Distributor can login**:
   - Go to `/accounts/distributor/login/`
   - Enter mobile number: `9876543210`
   - Enter password: `Dist@2026`
   - Access distributor dashboard

5. **Admin assigns QR codes** (optional):
   - Go to QR Dashboard
   - Generate batch with "Distributor" category
   - Assign to distributor user

6. **Distributor activates QRs**:
   - Users scan QR code
   - Make one-time payment
   - Activate QR code
   - Use unlimited free (no deductions)

## Important Notes

### Password Security
- Use strong passwords (mix of letters, numbers, symbols)
- Don't share passwords via insecure channels
- Consider using a password manager
- Change passwords if compromised

### Verification Process
- Only verify legitimate distributors
- Check their details before approval
- Verify phone number is correct
- Ensure they understand the system

### QR Code Assignment
- Distributors need QR codes to work
- Assign batches with "Distributor" category
- Monitor their activation rates
- Track revenue and payments

### Payment Flow
- Users scan distributor QR code
- First time: Pay activation fee (one-time)
- After payment: Activate QR code
- Future use: Unlimited free access
- No wallet deductions for distributor category

## Troubleshooting

### "No distributors found"
- No one has registered yet
- Check filters (might be filtering out results)
- Clear search and try again

### Can't verify distributor
- Make sure password is at least 6 characters
- Check if already verified
- Refresh page and try again

### Distributor can't login
- Verify they're using correct phone number
- Check if distributor is verified (not pending)
- Try resetting their password
- Make sure they're using `/accounts/distributor/login/` (not regular login)

### Wrong phone number
- Can't change phone after registration
- Need to revoke and ask them to register again
- Or manually update in Django admin

## Quick Reference

### URLs
- **Distributor Management**: `/accounts/admin/distributors/`
- **Admin Dashboard**: `/accounts/admin/dashboard/`
- **Distributor Login**: `/accounts/distributor/login/`
- **Distributor Registration**: `/accounts/distributor/become/`

### Status Badges
- 🟡 **⏳ Pending**: Needs verification
- 🟢 **✓ Verified**: Approved and active

### Actions
- **Verify & Assign Password**: Approve pending distributor
- **Reset Password**: Change password for verified distributor
- **Revoke**: Remove distributor status

## Next Steps

After verifying distributors:
1. Assign them QR codes (Distributor category)
2. Monitor their activation rates
3. Track payments and revenue
4. Provide support as needed

## Support

If you need help:
1. Check this guide
2. Review distributor registration guides
3. Check Django admin for detailed user info
4. Contact technical support
