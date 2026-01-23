# Distributor Login Debug Guide

## Issue

After verifying distributor and assigning password, login says "password is wrong".

## Why This Happens

You're seeing the Django admin login page because:
1. You're logged in as **admin** (staff user)
2. After verifying distributor, you stay on admin pages
3. When you try to test distributor login, you need to **logout first**

## Solution

### Step 1: Logout from Admin

After verifying a distributor:
1. Click your profile/username in top right
2. Click "Logout"
3. Or go to `/accounts/logout/`

### Step 2: Go to Distributor Login

Go to: `/accounts/distributor/login/`

**NOT** the Django admin login at `/admin/login/`

### Step 3: Test Login

Use:
- **Phone**: The 10-digit mobile number (e.g., `9876543210`)
- **Password**: The password you assigned (e.g., `Test@123`)

## Testing Without Logout

If you want to test without logging out:

### Option 1: Use Incognito/Private Window

1. Open incognito/private browser window
2. Go to `/accounts/distributor/login/`
3. Test login there

### Option 2: Use Different Browser

1. Open different browser
2. Go to `/accounts/distributor/login/`
3. Test login there

### Option 3: Run Test Script

```bash
python test_distributor_login.py
```

This will:
- Show all distributors
- Let you test login credentials
- Tell you if password is correct
- Show detailed debug info

## Common Mistakes

### ❌ Wrong: Using Django Admin Login
```
URL: /admin/login/
This is for Django admin staff only!
```

### ✅ Correct: Using Distributor Login
```
URL: /accounts/distributor/login/
This is for distributors!
```

### ❌ Wrong: Using Email
```
Login with: admin@example.com
Distributors don't use email!
```

### ✅ Correct: Using Phone Number
```
Login with: 9876543210
Distributors use phone number!
```

## Debug Steps

### 1. Check if Password Was Set

Run the test script:
```bash
python test_distributor_login.py
```

Look for:
```
Has usable password: True
```

If it says `False`, password wasn't set correctly.

### 2. Check Console Output

When you verify distributor, check terminal for:
```
==================================================
✅ DISTRIBUTOR VERIFIED
   User: user@example.com
   Password set: YES
   Has usable password: True
   Verified: True
==================================================
```

### 3. Check Login Attempt

When you try to login, check terminal for:
```
==================================================
🔐 DISTRIBUTOR LOGIN ATTEMPT
   Phone entered: 9876543210
   Total distributors: 1
==================================================
   Checking: user@example.com - Phone: 9876543210
   ✓ MATCH FOUND!

==================================================
👤 USER FOUND
   Email: user@example.com
   Username: user_543210
   Verified: True
   Has password: True
==================================================

🔐 Attempting authentication...
   Username: user_543210
   Password length: 8

✅ Authentication SUCCESS!
```

If you see `❌ Authentication FAILED`, the password is wrong.

## Troubleshooting

### Issue: "Invalid phone number or password"

**Possible causes**:
1. Wrong phone number
2. Wrong password
3. User not verified
4. Password not set

**Solution**:
- Run test script to verify credentials
- Check console output for details
- Make sure you're using correct phone number
- Make sure you're using password you assigned

### Issue: "Pending admin verification"

**Cause**: Distributor not verified yet

**Solution**:
- Go to admin distributor management
- Click "Verify & Assign Password"
- Assign password
- Try login again

### Issue: Redirected to Django admin login

**Cause**: You're on wrong login page

**Solution**:
- Logout from admin
- Go to `/accounts/distributor/login/` (not `/admin/login/`)
- Use phone + password (not email)

### Issue: "Has usable password: False"

**Cause**: Password not set correctly

**Solution**:
1. Go to admin distributor management
2. Find the distributor
3. Click "Reset Password"
4. Enter new password
5. Try login again

## Complete Test Workflow

### 1. Verify Distributor (As Admin)

```
1. Login as admin
2. Go to /accounts/admin/distributors/
3. Find pending distributor
4. Click "Verify & Assign Password"
5. Enter password: Test@123
6. Click "Verify & Assign"
7. See success message
```

### 2. Check Console Output

```
==================================================
✅ DISTRIBUTOR VERIFIED
   User: user@example.com
   Password set: YES
   Has usable password: True
   Verified: True
==================================================
```

### 3. Logout from Admin

```
1. Click profile in top right
2. Click "Logout"
3. Or go to /accounts/logout/
```

### 4. Test Distributor Login

```
1. Go to /accounts/distributor/login/
2. Enter phone: 9876543210
3. Enter password: Test@123
4. Click "Login"
5. Should redirect to distributor dashboard
```

### 5. Check Console Output

```
==================================================
🔐 DISTRIBUTOR LOGIN ATTEMPT
   Phone entered: 9876543210
==================================================
   ✓ MATCH FOUND!

✅ Authentication SUCCESS!
```

## Quick Test Command

Run this to test without browser:

```bash
python test_distributor_login.py
```

Enter:
- Phone: `9876543210`
- Password: `Test@123`

It will tell you if credentials are correct.

## Important Notes

### Different Login Pages

**Admin Login** (`/admin/login/`):
- For Django admin staff
- Uses email + password
- Access to admin panel

**Distributor Login** (`/accounts/distributor/login/`):
- For distributors only
- Uses phone + password
- Access to distributor dashboard

**Regular User Login** (`/accounts/login/`):
- For regular users
- Uses phone + OTP
- Access to user dashboard

### Password Requirements

- Minimum 6 characters
- Can include letters, numbers, symbols
- Case-sensitive
- No spaces

### Phone Number Format

- Must be 10 digits
- No country code
- No spaces or dashes
- Example: `9876543210`

## Summary

The issue is likely that you're:
1. Still logged in as admin
2. On the wrong login page (`/admin/login/` instead of `/accounts/distributor/login/`)
3. Using wrong credentials

**Solution**:
1. Logout from admin
2. Go to `/accounts/distributor/login/`
3. Use phone number + assigned password
4. Check console output for debug info
5. Run test script to verify credentials

If still not working, run the test script and share the output!
