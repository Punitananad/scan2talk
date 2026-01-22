# Razorpay Payment Gateway - Production Fix

## Problem
- Razorpay works on localhost but not on production (scan2talk.in)
- Order page shows "Order received! We will contact you for payment details" instead of Razorpay checkout

## Root Cause
The `.env` file with Razorpay credentials is not loaded on the production server, or the Django application hasn't been restarted after adding credentials.

## Solution

### Step 1: Verify Local Configuration
Run the diagnostic script locally first:
```bash
python check_razorpay_config.py
```

This should show:
- ✓ Razorpay client initialized successfully
- ✓ All credentials loaded

### Step 2: Check Production Server

#### Option A: SSH into Production
```bash
ssh your-server

# Navigate to project directory
cd /path/to/scan2talk

# Run diagnostic
python check_razorpay_config.py
```

#### Option B: Check via Django Shell
```bash
python manage.py shell
```

Then run:
```python
from apps.accounts.razorpay_service import RazorpayGatewayService
service = RazorpayGatewayService()
print("Client initialized:", service.client is not None)
print("Key ID:", service.key_id[:10] + "..." if service.key_id else "EMPTY")
```

### Step 3: Fix Production Configuration

#### If .env file is missing:
1. Copy `.env` file to production server:
```bash
scp .env your-server:/path/to/scan2talk/
```

2. Verify file permissions:
```bash
chmod 600 .env
```

#### If .env exists but not loaded:
1. Check if `python-dotenv` is installed:
```bash
pip list | grep python-dotenv
```

2. If not installed:
```bash
pip install python-dotenv
```

3. Verify `settings.py` loads `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 4: Restart Django Application

Choose the method that matches your setup:

#### Gunicorn:
```bash
sudo systemctl restart gunicorn
# OR
sudo systemctl restart gunicorn.service
```

#### uWSGI:
```bash
sudo systemctl restart uwsgi
```

#### Manual restart:
```bash
pkill -HUP gunicorn
```

#### Docker:
```bash
docker-compose restart web
```

### Step 5: Verify Fix

1. Visit: https://scan2talk.in/order-tag/
2. Fill in order details
3. Click "Proceed to Payment"
4. You should see Razorpay checkout page (not success message)

## Razorpay Credentials

Your live credentials (from `.env`):
```
RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS
RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO
RAZORPAY_WEBHOOK_SECRET=scan2talk_rzp_webhook_live_2026
```

## Troubleshooting

### Issue: "Razorpay client NOT initialized"
**Solution:** 
- Ensure `.env` file exists on production
- Restart Django application
- Check file permissions (should be readable by Django user)

### Issue: "Module 'razorpay' not found"
**Solution:**
```bash
pip install razorpay
```

### Issue: Still showing success message instead of payment
**Solution:**
1. Check Django logs for errors:
```bash
tail -f /var/log/gunicorn/error.log
# OR
journalctl -u gunicorn -f
```

2. Look for "Razorpay credentials not configured" warning

3. Verify environment variables are loaded:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('RAZORPAY_KEY_ID'))"
```

### Issue: Payment page loads but shows error
**Solution:**
- Check Razorpay dashboard for API errors
- Verify key_id starts with `rzp_live_` (not `rzp_test_`)
- Ensure key_secret is correct

## Quick Deploy Scripts

### Linux/Mac:
```bash
chmod +x deploy_razorpay_fix.sh
./deploy_razorpay_fix.sh
```

### Windows:
```powershell
.\deploy_razorpay_fix.ps1
```

## Testing Checklist

- [ ] Diagnostic script shows ✓ for all checks
- [ ] Django application restarted
- [ ] Order page loads correctly
- [ ] "Proceed to Payment" shows Razorpay checkout
- [ ] Test payment completes successfully
- [ ] Order saved to database with status "completed"

## Support

If issues persist:
1. Check Django logs
2. Check Razorpay dashboard for API calls
3. Verify webhook URL is configured (if using webhooks)
4. Test with a small amount (₹1) first

## Files Created
- `check_razorpay_config.py` - Diagnostic script
- `deploy_razorpay_fix.sh` - Linux/Mac deployment
- `deploy_razorpay_fix.ps1` - Windows deployment
- `RAZORPAY_PRODUCTION_FIX.md` - This guide
