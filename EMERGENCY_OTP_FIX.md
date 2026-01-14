# 🚨 EMERGENCY OTP FIX - Production Not Receiving SMS

## 🔥 IMMEDIATE ACTIONS (Do These NOW)

### Step 1: Run Diagnostic (2 minutes)
```bash
# On production server
python diagnose_otp_production.py
```

This will:
- Check credentials
- Test actual API call
- Show exact error message
- Give specific troubleshooting steps

### Step 2: Verify DLT Template (1 minute)
```bash
python verify_dlt_template.py
```

This will:
- Show character-by-character comparison
- Identify invisible character differences
- Tell you if template matches

### Step 3: Check These Common Issues

#### Issue A: Wrong Credentials
```bash
# Check .env on production
cat .env | grep SMSCOUNTRY

# Should show:
SMSCOUNTRY_AUTH_KEY=qQbyH5R7gFfxivRgYA0dANd
SMSCOUNTRY_AUTH_TOKEN=NXMG6GLXdUqWqJY7QD6u2oGivqHDHOVK85w3aLT0
```

#### Issue B: Code Not Deployed
```bash
# Check if new code is deployed
grep "Accounts/{self.auth_key}" apps/communications/otp_service.py

# Should show the account-scoped endpoint
```

#### Issue C: Server Not Restarted
```bash
# Restart Django/Gunicorn
sudo systemctl restart gunicorn
# OR
sudo supervisorctl restart all
# OR
pkill -f gunicorn && gunicorn ...
```

---

## 🔍 MOST LIKELY CAUSES

### 1. Code Not Deployed Yet (90% probability)
**Problem:** You fixed the code locally but didn't deploy to production

**Check:**
```bash
# On production server
cd /path/to/project
git log -1 --oneline
# Should show recent commit with OTP fix
```

**Fix:**
```bash
# Deploy the changes
git pull origin main
sudo systemctl restart gunicorn
```

### 2. DLT Template Mismatch (5% probability)
**Problem:** Template text has invisible character differences

**Check:** Run `python verify_dlt_template.py`

**Fix:** Copy EXACT text from DLT portal

### 3. Sender ID Not Approved (3% probability)
**Problem:** SCNTLK not approved for your account

**Check:** Login to SMSCountry dashboard → Sender IDs

**Fix:** Request approval or use different sender ID

### 4. Account Balance Zero (2% probability)
**Problem:** No credits in SMSCountry account

**Check:** Login to SMSCountry dashboard → Balance

**Fix:** Recharge account

---

## 🚀 QUICK FIX OPTIONS

### Option 1: Deploy Fixed Code (RECOMMENDED)
```bash
# On your local machine
git add apps/communications/otp_service.py
git commit -m "Fix OTP delivery - use account-scoped endpoint"
git push origin main

# On production server
cd /path/to/project
git pull origin main
sudo systemctl restart gunicorn

# Test immediately
python diagnose_otp_production.py
```

### Option 2: Manual Fix on Production (IF URGENT)
```bash
# On production server
nano apps/communications/otp_service.py

# Find line:
#   API_ENDPOINT = "https://restapi.smscountry.com/v0.1/SMSes/"

# Replace with:
#   # Endpoint set in __init__ based on auth_key

# Find __init__ method and ensure it has:
#   if self.auth_key:
#       self.api_endpoint = f"https://restapi.smscountry.com/v0.1/Accounts/{self.auth_key}/SMSes/"

# Save and restart
sudo systemctl restart gunicorn
```

### Option 3: Test with curl (VERIFY API WORKS)
```bash
# Replace YOUR_AUTH_KEY and YOUR_AUTH_TOKEN
AUTH_KEY="qQbyH5R7gFfxivRgYA0dANd"
AUTH_TOKEN="NXMG6GLXdUqWqJY7QD6u2oGivqHDHOVK85w3aLT0"
PHONE="9876543210"  # Your test number

# Create base64 auth
AUTH=$(echo -n "$AUTH_KEY:$AUTH_TOKEN" | base64)

# Test API call
curl -X POST "https://restapi.smscountry.com/v0.1/Accounts/$AUTH_KEY/SMSes/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $AUTH" \
  -d "{
    \"Text\": \"Your OTP for Scan2Talk website registration is 123456. Do not share it with anyone. - Scan2Talk\",
    \"Number\": \"91$PHONE\",
    \"SenderId\": \"SCNTLK\",
    \"DLTTemplateId\": \"1707176830112398745\",
    \"Tool\": \"API\"
  }"
```

**Expected Response:**
```json
{
  "Success": true,
  "Message": "Message sent successfully",
  "MessageUUID": "..."
}
```

---

## 📊 DEBUGGING CHECKLIST

Run through this checklist:

- [ ] Credentials in .env are correct
- [ ] Code has account-scoped endpoint
- [ ] Server has been restarted
- [ ] DLT template text matches exactly
- [ ] Sender ID SCNTLK is approved
- [ ] Account has sufficient balance
- [ ] curl test works and returns Success: true
- [ ] Phone number is not DND
- [ ] Test with different phone number
- [ ] Check SMSCountry dashboard for delivery status

---

## 🔧 ALTERNATIVE: Use Different SMS Provider

If SMSCountry keeps failing, switch to alternative:

### Option A: Twilio (Fastest)
```python
# In otp_service.py, add fallback
from twilio.rest import Client

def send_otp_twilio(self, phone_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP is {otp}. Valid for 5 minutes.",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{phone_number}"
    )
    return True, otp, "OTP sent via Twilio"
```

### Option B: MSG91
```python
def send_otp_msg91(self, phone_number, otp):
    url = "https://api.msg91.com/api/v5/otp"
    payload = {
        "template_id": "YOUR_TEMPLATE_ID",
        "mobile": f"91{phone_number}",
        "otp": otp
    }
    headers = {"authkey": settings.MSG91_AUTH_KEY}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200
```

---

## 📞 CONTACT SMSCOUNTRY SUPPORT

If nothing works, contact them:

**Email:** support@smscountry.com
**Phone:** Check their website

**What to tell them:**
1. "OTP SMS not being delivered"
2. "Using account-scoped endpoint: /Accounts/{AuthKey}/SMSes/"
3. "Getting HTTP 200 but Success: false"
4. "DLT Template ID: 1707176830112398745"
5. "Sender ID: SCNTLK"
6. "Need help debugging delivery issue"

---

## ✅ VERIFICATION STEPS

After applying fix:

1. **Test OTP Flow:**
   ```bash
   # On production
   python diagnose_otp_production.py
   ```

2. **Check Logs:**
   ```bash
   tail -f /var/log/gunicorn/error.log
   # Look for "✅ OTP sent successfully"
   ```

3. **Test Real Activation:**
   - Scan QR code
   - Enter phone number
   - Check if OTP arrives within 10 seconds

4. **Verify in SMSCountry Dashboard:**
   - Login to dashboard
   - Check "SMS Reports"
   - Verify delivery status

---

## 🎯 SUCCESS INDICATORS

You'll know it's working when:

✅ `diagnose_otp_production.py` shows "Success: true"
✅ SMS arrives within 5-10 seconds
✅ Logs show "✅ OTP sent successfully, MessageID: ..."
✅ SMSCountry dashboard shows "Delivered"

---

## 💡 PREVENTION

To avoid this in future:

1. **Always test on staging first**
2. **Use diagnostic script before deploying**
3. **Monitor SMS delivery rates**
4. **Set up alerts for failed OTPs**
5. **Keep backup SMS provider configured**

---

**Last Updated:** January 15, 2026  
**Priority:** 🚨 CRITICAL  
**Status:** Awaiting production deployment
