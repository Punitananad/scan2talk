# Quick SSH and Deploy Guide

## Step 1: SSH into Production Server

From your Windows terminal, run:

```bash
ssh root@68.183.91.15
```

Or if you have a domain:
```bash
ssh root@scan2talk.in
```

## Step 2: Navigate to Project

```bash
cd /var/www/scan2talk
```

## Step 3: Run Deployment Script

```bash
sudo bash ramban_deploy_s2t.sh
```

## Alternative: Manual Deployment Steps

If the script doesn't work, run these commands one by one:

```bash
# 1. Navigate to project
cd /var/www/scan2talk

# 2. Backup database
mkdir -p backups
cp db.sqlite3 backups/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# 3. Pull latest code
git stash
git pull origin main

# 4. Activate virtual environment
source /var/www/venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Run migrations
python manage.py migrate

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 9. Check status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## Troubleshooting

If you get disconnected, just SSH back in:
```bash
ssh root@68.183.91.15
```

If you need the password, check your server credentials.

## Quick Status Check

```bash
# Check if services are running
sudo systemctl status gunicorn
sudo systemctl status nginx

# View recent logs
sudo journalctl -u gunicorn -n 50
```
