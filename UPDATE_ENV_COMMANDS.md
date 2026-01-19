# Commands to Update .env in Production

## Option 1: Automated Script (Recommended)

Run the automated script from your local machine:

```bash
bash update_spartan_env.sh
```

This will:
1. SSH into production server
2. Backup current .env file
3. Update Spartan credentials
4. Restart services
5. Show confirmation

---

## Option 2: Manual SSH Commands

### Step 1: SSH into Production Server
```bash
ssh ramban@103.127.29.78
```

### Step 2: Navigate to Project Directory
```bash
cd /home/ramban/gateway_platform
```

### Step 3: Backup Current .env
```bash
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

### Step 4: Edit .env File
```bash
nano .env
```

Find and update these lines:
```bash
SPARKTG_USERNAME=10215500
SPARKTG_PASSWORD=Admin@007
SPARKTG_SID=2155
SPARKTG_DID_NUMBER=01205018960
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Step 5: Verify Changes
```bash
grep "^SPARKTG_" .env
```

### Step 6: Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Step 7: Check Service Status
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

---

## Option 3: One-Line SSH Command

Update all Spartan credentials in one command:

```bash
ssh ramban@103.127.29.78 "cd /home/ramban/gateway_platform && cp .env .env.backup.\$(date +%Y%m%d_%H%M%S) && sed -i 's/^SPARKTG_USERNAME=.*/SPARKTG_USERNAME=10215500/' .env && sed -i 's/^SPARKTG_PASSWORD=.*/SPARKTG_PASSWORD=Admin@007/' .env && sed -i 's/^SPARKTG_SID=.*/SPARKTG_SID=2155/' .env && (grep -q '^SPARKTG_DID_NUMBER=' .env && sed -i 's/^SPARKTG_DID_NUMBER=.*/SPARKTG_DID_NUMBER=01205018960/' .env || echo 'SPARKTG_DID_NUMBER=01205018960' >> .env) && grep '^SPARKTG_' .env && sudo systemctl restart gunicorn && sudo systemctl restart nginx && echo '✅ Done!'"
```

---

## Option 4: Using sed Commands Only

If you're already SSH'd into the server:

```bash
# Navigate to project
cd /home/ramban/gateway_platform

# Backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update credentials
sed -i 's/^SPARKTG_USERNAME=.*/SPARKTG_USERNAME=10215500/' .env
sed -i 's/^SPARKTG_PASSWORD=.*/SPARKTG_PASSWORD=Admin@007/' .env
sed -i 's/^SPARKTG_SID=.*/SPARKTG_SID=2155/' .env

# Add or update DID number
if grep -q "^SPARKTG_DID_NUMBER=" .env; then
    sed -i 's/^SPARKTG_DID_NUMBER=.*/SPARKTG_DID_NUMBER=01205018960/' .env
else
    echo "SPARKTG_DID_NUMBER=01205018960" >> .env
fi

# Verify
grep "^SPARKTG_" .env

# Restart
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## Option 5: Using PowerShell (Windows)

From your Windows machine:

```powershell
# Run the PowerShell deployment script
.\deploy_from_windows.ps1
```

Or manually:

```powershell
# SSH and update
ssh ramban@103.127.29.78 @"
cd /home/ramban/gateway_platform
cp .env .env.backup.`$(date +%Y%m%d_%H%M%S)
sed -i 's/^SPARKTG_USERNAME=.*/SPARKTG_USERNAME=10215500/' .env
sed -i 's/^SPARKTG_PASSWORD=.*/SPARKTG_PASSWORD=Admin@007/' .env
sed -i 's/^SPARKTG_SID=.*/SPARKTG_SID=2155/' .env
grep -q '^SPARKTG_DID_NUMBER=' .env && sed -i 's/^SPARKTG_DID_NUMBER=.*/SPARKTG_DID_NUMBER=01205018960/' .env || echo 'SPARKTG_DID_NUMBER=01205018960' >> .env
sudo systemctl restart gunicorn
sudo systemctl restart nginx
"@
```

---

## Verification Commands

After updating, verify the changes:

```bash
# Check if credentials are updated
ssh ramban@103.127.29.78 "cd /home/ramban/gateway_platform && grep '^SPARKTG_' .env"

# Check service status
ssh ramban@103.127.29.78 "sudo systemctl status gunicorn | head -n 10"

# Check Django can read the settings
ssh ramban@103.127.29.78 "cd /home/ramban/gateway_platform && source venv/bin/activate && python manage.py shell -c 'from django.conf import settings; print(f\"Username: {settings.SPARKTG_USERNAME}\"); print(f\"DID: {settings.SPARKTG_DID_NUMBER}\")'"
```

---

## Troubleshooting

### If services don't restart:
```bash
ssh ramban@103.127.29.78
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

### If .env changes don't take effect:
```bash
# Make sure to restart gunicorn (not just reload)
sudo systemctl restart gunicorn

# Check if .env is being read
cd /home/ramban/gateway_platform
source venv/bin/activate
python manage.py shell
>>> from django.conf import settings
>>> settings.SPARKTG_USERNAME
>>> settings.SPARKTG_DID_NUMBER
```

### Restore from backup if needed:
```bash
cd /home/ramban/gateway_platform
ls -la .env.backup.*
cp .env.backup.YYYYMMDD_HHMMSS .env
sudo systemctl restart gunicorn
```

---

## Quick Reference

**New Spartan Credentials:**
- Username: `10215500`
- Password: `Admin@007`
- Service ID: `2155`
- DID Number: `01205018960`

**Production Server:**
- Host: `103.127.29.78`
- User: `ramban`
- Project Path: `/home/ramban/gateway_platform`

**Services to Restart:**
- `gunicorn` (Django app)
- `nginx` (web server)
