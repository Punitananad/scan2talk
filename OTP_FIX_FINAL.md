# OTP Fix + User Profile Balance - Complete

## Changes Made

### 1. OTP Service - Removed DLT Template Requirement
**File:** `apps/communications/otp_service.py`

**Removed:**
- DLT Template ID requirement
- Fixed template text requirement

**Now Uses:**
- Simple OTP message: "Your OTP is {otp}. Valid for 5 minutes. - Scan2Talk"
- No template validation
- Works with any SMSCountry account

### 2. User Profile - Added Wallet Balance Display
**Files:** 
- `templates/accounts/profile.html`
- `apps/accounts/views.py`

**Added:**
- Total wallet balance across all user's QR codes
- Large, prominent display: ₹XX.XX
- Direct recharge button
- Calculates sum of all QRWallet balances for user

## Deploy Commands

```bash
git add apps/communications/otp_service.py apps/accounts/views.py templates/accounts/profile.html
git commit -m "Fix OTP delivery + add user wallet balance to profile"
git push origin main

# On production
git pull origin main
sudo systemctl restart gunicorn
```

## Test OTP

```bash
python diagnose_otp_production.py
```

Should now work without DLT template errors.

## User Profile

Visit: `/accounts/profile/`

Shows:
- Total wallet balance (sum of all QR wallets)
- User categories
- Quick recharge button
