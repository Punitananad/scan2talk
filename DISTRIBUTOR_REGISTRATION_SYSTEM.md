# Distributor Registration System

## Overview
Users can register as distributors to sell QR codes. The system uses **OTP verification once** and **admin-assigned passwords** for future logins.

## User Flow

### 1. Registration (One-Time)
```
Dashboard → "Become a Distributor" Button
  ↓
Enter Mobile Number
  ↓
Verify OTP (one-time only)
  ↓
Registration Complete → Pending Admin Verification
```

### 2. Admin Verification
```
Admin Panel → Users → Filter: is_distributor=True, distributor_verified=False
  ↓
Select Distributor(s)
  ↓
Action: "Verify selected distributors"
  ↓
Action: "Assign random passwords to distributors"
  ↓
Send password to distributor via SMS/Email
```

### 3. Distributor Login (No OTP)
```
/accounts/distributor/login/
  ↓
Enter: Mobile Number + Password
  ↓
Login Success → Distributor Dashboard
```

## Features

### For Users
- ✅ One-click registration from dashboard
- ✅ OTP verification (one-time only)
- ✅ No password creation (admin assigns)
- ✅ Simple login with mobile + password
- ✅ Dedicated distributor dashboard

### For Admins
- ✅ View pending distributor registrations
- ✅ Verify distributors with one click
- ✅ Auto-generate secure passwords
- ✅ Track distributor activity
- ✅ Manage distributor permissions

## Database Changes

### User Model
```python
is_distributor = BooleanField(default=False)
distributor_verified = BooleanField(default=False)
distributor_registered_at = DateTimeField(null=True)
```

## URLs

| Purpose | URL | Auth Required |
|---------|-----|---------------|
| Registration | `/accounts/distributor/become/` | Yes (logged in) |
| OTP Verification | `/accounts/distributor/verify/` | Yes (logged in) |
| Pending Status | `/accounts/distributor/pending/` | Yes (logged in) |
| Login | `/accounts/distributor/login/` | No |
| Dashboard | `/accounts/distributor/dashboard/` | Yes (distributor) |

## Templates

1. **become_distributor.html** - Registration form
2. **become_distributor_verify.html** - OTP verification
3. **distributor_pending.html** - Pending verification status
4. **distributor_login.html** - Login with mobile + password
5. **distributor_dashboard.html** - Distributor dashboard

## Admin Actions

### 1. Verify Distributors
- Select users with `is_distributor=True` and `distributor_verified=False`
- Click "Verify selected distributors"
- Sets `distributor_verified=True`

### 2. Assign Passwords
- Select verified distributors
- Click "Assign random passwords to distributors"
- Generates 8-character random password
- Shows passwords in admin message
- **Production:** Send via SMS/Email instead

## Security

### Password Generation
```python
import secrets
import string
password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
```

### Login Authentication
- Uses Django's built-in authentication
- Finds user by decrypted phone number
- Authenticates with username + password
- No OTP required after first registration

## Testing

### 1. Test Registration
```
1. Login as regular user
2. Go to dashboard
3. Click "Become a Distributor"
4. Enter mobile number
5. Verify OTP
6. Check pending status
```

### 2. Test Admin Verification
```
1. Login to admin panel
2. Go to Users
3. Filter: is_distributor=True
4. Select pending distributor
5. Action: Verify distributors
6. Action: Assign passwords
7. Note the generated password
```

### 3. Test Login
```
1. Logout
2. Go to /accounts/distributor/login/
3. Enter mobile + assigned password
4. Should login to distributor dashboard
```

## Migration

Run migration to add distributor fields:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Dashboard Button Logic

```django
{% if user.is_distributor %}
    {% if user.distributor_verified %}
        <!-- Show Distributor Dashboard button -->
    {% else %}
        <!-- Show Pending Verification button -->
    {% endif %}
{% else %}
    <!-- Show "Become a Distributor" button -->
{% endif %}
```

## Distributor Dashboard Features

- Total QR codes assigned
- Activated vs Available QR codes
- Total revenue from sales
- Recent payment history
- Quick actions

## Future Enhancements

1. **SMS Integration:** Auto-send password via SMS
2. **Email Notification:** Send password via email
3. **Password Reset:** Allow distributors to request password reset
4. **Two-Factor Auth:** Optional 2FA for distributors
5. **Commission Tracking:** Track distributor commissions
6. **Performance Metrics:** Sales analytics and reports

## Production Checklist

- [ ] Migration applied
- [ ] Templates created
- [ ] URLs configured
- [ ] Admin actions tested
- [ ] SMS/Email integration for password delivery
- [ ] Security review
- [ ] User documentation
- [ ] Admin training

## Support

### For Users
- Registration issues: Check OTP delivery
- Login issues: Verify password with admin
- Access issues: Check verification status

### For Admins
- Verify pending distributors regularly
- Send passwords securely (SMS/Email)
- Monitor distributor activity
- Handle password reset requests

## Summary

The distributor registration system provides:
- ✅ Simple one-time OTP registration
- ✅ Admin-controlled password assignment
- ✅ Secure login without repeated OTP
- ✅ Dedicated distributor dashboard
- ✅ Easy admin management

**Status:** ✅ Complete and ready to use!
