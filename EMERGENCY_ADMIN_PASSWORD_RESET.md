# 🚨 EMERGENCY: Admin Password Reset on Production

## CRITICAL ISSUE

Your admin password was changed when verifying a distributor. You need to reset it immediately.

## Quick Fix (SSH Required)

### Method 1: Using Django Management Command

```bash
# SSH into production server
ssh root@your-server-ip

# Navigate to project
cd /var/www/scan2talk  # or wherever your project is

# Activate virtual environment (if using one)
source venv/bin/activate

# Reset password
python manage.py changepassword admin@scan2talk.in
```

It will prompt you to enter a new password twice.

### Method 2: Using Django Shell

```bash
# SSH into production server
ssh root@your-server-ip

# Navigate to project
cd /var/www/scan2talk

# Activate virtual environment
source venv/bin/activate

# Open Django shell
python manage.py shell
```

Then run this Python code:

```python
from apps.accounts.models import User

# Replace with your actual admin email
admin = User.objects.get(email='admin@scan2talk.in')

# Set new password (replace with your desired password)
admin.set_password('NewSecurePassword123!')
admin.save()

print(f"✅ Password reset successfully for {admin.email}")
exit()
```

### Method 3: Create Superuser (If Above Fails)

```bash
python manage.py createsuperuser
```

Follow the prompts to create a new admin account.

## After Resetting Password

1. Try logging in at: `https://scan2talk.in/admin/`
2. Use your new password
3. Once logged in, you can manage distributors again

## Why This Happened

The `verify_distributor` function should only change the distributor's password, not yours. There might be:

1. A bug in the code
2. Wrong user_id being passed
3. Session confusion

## Prevention

I'll fix the code to add extra safety checks to prevent this from happening again.

## Need Help?

If you can't SSH into the server:
1. Contact your hosting provider
2. Use their control panel to access the server
3. Or use their database management tool to reset the password directly

## Database Direct Reset (Last Resort)

If you have database access:

```sql
-- Find your admin user
SELECT id, email, username FROM users WHERE is_staff = true;

-- Note: You can't set password directly in database
-- You must use Django's set_password() method
```

## Contact Info

If you're stuck, you need to:
1. Access your production server via SSH
2. Run the Django shell commands above
3. Reset your admin password

This is a critical security issue that needs immediate attention!
