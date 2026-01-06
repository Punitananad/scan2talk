# Production Deployment Guide - Ubuntu + Nginx + Gunicorn

## Server Requirements
- Ubuntu 20.04 or 22.04
- Python 3.8+
- Nginx
- PostgreSQL (recommended) or SQLite
- Domain name (optional but recommended)

## Step 1: Initial Server Setup

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib git
```

## Step 2: Clone Repository

```bash
# Navigate to web directory
cd /var/www

# Clone your repository
sudo git clone https://github.com/Punitananad/scan2talk.git
cd scan2talk

# Set permissions
sudo chown -R $USER:$USER /var/www/scan2talk
```

## Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install gunicorn
pip install gunicorn
```

## Step 4: Create .env File

```bash
# Create .env file
nano .env
```

**Add your environment variables:**

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://dbuser:dbpassword@localhost:5432/scan2talk

# Or use SQLite for testing
# DATABASE_URL=sqlite:///db.sqlite3

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp (optional)
WHATSAPP_BUSINESS_API_TOKEN=your-whatsapp-token
WHATSAPP_BUSINESS_PHONE_ID=your-phone-id

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key

# Platform
PLATFORM_DOMAIN=your-domain.com
MAX_GATEWAYS_PER_USER=100

# CORS (if needed)
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

**Generate SECRET_KEY:**
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 5: Setup PostgreSQL Database (Recommended)

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE scan2talk;
CREATE USER scan2talk_user WITH PASSWORD 'your-strong-password';
ALTER ROLE scan2talk_user SET client_encoding TO 'utf8';
ALTER ROLE scan2talk_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE scan2talk_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE scan2talk TO scan2talk_user;
\q
```

**Update .env with database credentials:**
```env
DATABASE_URL=postgresql://scan2talk_user:your-strong-password@localhost:5432/scan2talk
```

## Step 6: Run Django Migrations

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Create required directories
mkdir -p logs media/qr_codes static
```

## Step 7: Test Gunicorn

```bash
# Test if gunicorn works
gunicorn --bind 0.0.0.0:8000 gateway_platform.wsgi:application

# If it works, press Ctrl+C to stop
```

## Step 8: Create Gunicorn Systemd Service

```bash
# Create gunicorn service file
sudo nano /etc/systemd/system/gunicorn.service
```

**Add this content:**

```ini
[Unit]
Description=Gunicorn daemon for scan2talk
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/scan2talk
Environment="PATH=/var/www/scan2talk/venv/bin"
ExecStart=/var/www/scan2talk/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/scan2talk/gunicorn.sock \
          --timeout 120 \
          --access-logfile /var/www/scan2talk/logs/gunicorn-access.log \
          --error-logfile /var/www/scan2talk/logs/gunicorn-error.log \
          gateway_platform.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Set permissions:**
```bash
sudo chown -R www-data:www-data /var/www/scan2talk
sudo chmod -R 755 /var/www/scan2talk
```

**Start and enable service:**
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## Step 9: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/scan2talk
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/ {
        alias /var/www/scan2talk/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/scan2talk/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/scan2talk/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable the site:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/scan2talk /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 10: Setup SSL with Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**Certbot will automatically update your Nginx config to use HTTPS!**

## Step 11: Configure Firewall

```bash
# Allow Nginx
sudo ufw allow 'Nginx Full'

# Allow SSH (if not already allowed)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 12: Update Django Settings for Production

Make sure your `settings.py` has:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'your-server-ip']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Step 13: Setup Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/scan2talk
```

**Add:**
```
/var/www/scan2talk/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
```

## Step 14: Setup Monitoring (Optional)

```bash
# Install monitoring tools
sudo apt install -y htop

# Check logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/www/scan2talk/logs/gunicorn-error.log
sudo tail -f /var/nginx/error.log
```

## Useful Commands

### Restart Services
```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### Update Code
```bash
cd /var/www/scan2talk
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### View Logs
```bash
# Gunicorn logs
sudo tail -f /var/www/scan2talk/logs/gunicorn-error.log
sudo tail -f /var/www/scan2talk/logs/gunicorn-access.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs
sudo tail -f /var/www/scan2talk/logs/django.log

# System logs
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f
```

### Database Backup
```bash
# PostgreSQL backup
pg_dump -U scan2talk_user scan2talk > backup_$(date +%Y%m%d).sql

# Restore
psql -U scan2talk_user scan2talk < backup_20260106.sql
```

## Troubleshooting

### Gunicorn won't start
```bash
# Check logs
sudo journalctl -u gunicorn -n 50

# Check permissions
ls -la /var/www/scan2talk

# Test manually
cd /var/www/scan2talk
source venv/bin/activate
gunicorn --bind 0.0.0.0:8000 gateway_platform.wsgi:application
```

### Nginx 502 Bad Gateway
```bash
# Check if gunicorn is running
sudo systemctl status gunicorn

# Check socket file exists
ls -la /var/www/scan2talk/gunicorn.sock

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Static files not loading
```bash
# Collect static files again
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/scan2talk/staticfiles
```

### Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U scan2talk_user -d scan2talk -h localhost
```

## Performance Optimization

### 1. Increase Gunicorn Workers
Edit `/etc/systemd/system/gunicorn.service`:
```ini
--workers 5  # (2 x CPU cores) + 1
```

### 2. Enable Gzip in Nginx
Add to nginx config:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### 3. Setup Redis for Caching
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```

Update `.env`:
```env
REDIS_URL=redis://localhost:6379/0
```

## Security Checklist

- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY
- ✅ HTTPS enabled (SSL certificate)
- ✅ Firewall configured
- ✅ Database password is strong
- ✅ .env file has restricted permissions (chmod 600)
- ✅ Regular backups configured
- ✅ Log rotation enabled
- ✅ Security headers enabled
- ✅ ALLOWED_HOSTS properly configured

## Quick Deployment Script

Save this as `deploy.sh`:

```bash
#!/bin/bash
cd /var/www/scan2talk
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart nginx
echo "Deployment complete!"
```

Make it executable:
```bash
chmod +x deploy.sh
```

## Your Site is Live! 🚀

Access your application at:
- **HTTP:** http://your-domain.com
- **HTTPS:** https://your-domain.com (after SSL setup)

Admin panel:
- https://your-domain.com/admin/

QR Dashboard:
- https://your-domain.com/gateways/qr/dashboard/

## Support

If you encounter issues:
1. Check logs (gunicorn, nginx, django)
2. Verify all services are running
3. Check file permissions
4. Ensure .env variables are correct
5. Test database connection

Good luck with your deployment! 🎉
