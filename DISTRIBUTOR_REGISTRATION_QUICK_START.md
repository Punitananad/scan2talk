# Distributor Registration - Quick Start Guide

## 🎯 What You Need to Know

The OTP **IS working** - it's just being printed to your terminal instead of sent via SMS because you're in DEBUG mode.

## 📋 Step-by-Step Instructions

### 1. Start Your Django Server

Open a terminal and run:
```bash
python manage.py runserver
```

**IMPORTANT**: Keep this terminal window visible!

### 2. Open Your Browser

Go to: `http://localhost:8000` or `http://127.0.0.1:8000`

### 3. Login and Go to Profile

- Login with your account
- Click on "My Profile" or go to your dashboard
- You'll see a "Become a Distributor" button

### 4. Click "Become a Distributor"

- Enter your 10-digit mobile number
- Click "Send OTP"

### 5. **LOOK AT YOUR TERMINAL** 👀

This is the most important step!

In the terminal where Django is running, you'll see something like:

```
==================================================
📱 OTP for 9876543210: 123456
==================================================
```

**That's your OTP!** Copy it (123456 in this example).

### 6. Enter the OTP

- Go back to your browser
- Paste the OTP you copied from terminal
- Click "Verify & Register"

### 7. Success!

You'll see a success message and be redirected to a pending page.

Now admin needs to:
- Verify your distributor account
- Assign you a password

## 🔧 If You Don't See OTP in Terminal

### Option 1: Run Diagnostic Test

```bash
python test_distributor_otp.py
```

Enter your phone number when prompted. The OTP will be shown.

### Option 2: Check Console Output

Look for these messages in terminal:
- `🔔 DISTRIBUTOR OTP REQUEST`
- `📤 OTP SEND RESULT`
- `📱 OTP for [phone]: [code]`

### Option 3: Try Resend

On the OTP verification page, click "Resend OTP" and check terminal again.

## 🎨 UI Features

### Navigation Bar
- **Desktop**: "Distributor Login" button in top navigation
- **Mobile**: "Distributor Login" in mobile menu

### Profile Page
- "Become a Distributor" button with purple gradient
- Shows if you're already a distributor

### Distributor Login
- Separate login page for distributors
- Uses mobile number + admin-assigned password
- No OTP needed after initial registration

## 👨‍💼 Admin Actions

After user registers, admin needs to:

1. Go to Django admin: `/admin/`
2. Go to Users section
3. Find the user who registered
4. Select the user
5. Choose action: "Verify distributor and assign password"
6. Enter a secure password
7. Click "Go"

The user can now login at `/accounts/distributor/login/` with:
- Mobile number
- Admin-assigned password

## 📊 Distributor Dashboard

After admin verification, distributor can:
- View assigned QR codes
- See activation statistics
- Track payments
- Monitor revenue

## 🐛 Troubleshooting

### "Session expired" error
- Start over from step 3
- Don't wait too long between steps

### "Invalid OTP" error
- Make sure you copied the correct OTP from terminal
- Check if you're looking at the latest OTP (if you clicked resend)
- OTP expires after 5 minutes

### "Too many failed attempts"
- Wait 2 hours or contact admin to reset
- Or run: `python manage.py shell` and clear cache

### OTP not in terminal
- Make sure Django server is running in terminal (not background)
- Check if terminal is scrolled up - scroll to bottom
- Try the diagnostic test: `python test_distributor_otp.py`

## 📱 Why SMS Not Coming?

In DEBUG mode (`DEBUG=True` in `.env`):
- OTP is printed to console instead of SMS
- This is **intentional** for development
- Allows testing without SMS credits
- Allows testing even if SMS API has issues

In PRODUCTION mode (`DEBUG=False`):
- OTP will be sent via SMS
- Must have working SMSCountry credentials
- Must have SMS credits

## ✅ Success Indicators

You know it's working when you see:

1. **In Terminal**:
   ```
   📤 OTP SEND RESULT
      Success: True
      Message: OTP generated (dev mode - not sent)
   ```

2. **In Browser**:
   - "OTP sent to your mobile number" message
   - Redirected to verification page

3. **After Verification**:
   - "🎉 Distributor registration successful!" message
   - Redirected to pending page

## 🚀 What's Next?

1. **User**: Wait for admin to verify and assign password
2. **Admin**: Verify distributor and assign password
3. **User**: Login at `/accounts/distributor/login/`
4. **User**: Access distributor dashboard

## 📞 Need Help?

Read the detailed guides:
- `DISTRIBUTOR_OTP_DEBUG_GUIDE.md` - Comprehensive debugging
- `DISTRIBUTOR_OTP_FIX.md` - Technical details
- Run `python test_distributor_otp.py` - Interactive test

## 🎉 That's It!

The system is working correctly. Just remember to **look at the terminal** for the OTP!
