#!/bin/bash

# Scan2Talk Initial Server Setup Script
# Run this ONCE on a fresh Ubuntu server

set -e

echo "🔧 Starting initial server setup for Scan2Talk..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib git curl

# Install certbot for SSL
print_status "Installing Certbot for SSL..."
apt install -y certbot python3-certbot-nginx

# Create project directory
print_status "Creating project directory..."
mkdir -p /var/www
cd /var/www

# Clone repository
print_status "Cloning repository..."
if [ -d "scan2talk" ]; then
    print_warning "Directory already exists, skipping clone"
else
    git clone https://github.com/Punitananad/scan2talk.git
fi

cd scan2talk

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv

# Activate and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create directories
print_status "Creating required directories..."
mkdir -p logs media/qr_codes static

# Setup PostgreSQL
print_status "Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE scan2talk;" 2>/dev/null || print_warning "Database already exists"
sudo -u postgres psql -c "CREATE USER scan2talk_user WITH PASSWORD 'changeme123';" 2>/dev/null || print_warning "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE scan2talk TO scan2talk_user;"

# Create .env template
print_status "Creating .env template..."
cat > .env << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=CHANGE-THIS-TO-A-RANDOM-SECRET-KEY
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database
DATABASE_URL=postgresql://scan2talk_user:changeme123@localhost:5432/scan2talk

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp (optional)
WHATSAPP_BUSINESS_API_TOKEN=
WHATSAPP_BUSINESS_PHONE_ID=

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key

# Platform
PLATFORM_DOMAIN=your-domain.com
MAX_GATEWAYS_PER_USER=100
EOF

print_warning "⚠️  IMPORTANT: Edit /var/www/scan2talk/.env with your actual values!"

# Create Gunicorn service
print_status "Creating Gunicorn systemd service..."
cat > /etc/systemd/system/gunicorn.service << 'EOF'
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
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/scan2talk << 'EOF'
server {
    listen 80;
    server_name _;

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
EOF

# Enable Nginx site
print_status "Enabling Nginx site..."
ln -sf /etc/nginx/sites-available/scan2talk /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Set permissions
print_status "Setting permissions..."
chown -R www-data:www-data /var/www/scan2talk
chmod -R 755 /var/www/scan2talk
chmod 600 /var/www/scan2talk/.env

# Test Nginx configuration
print_status "Testing Nginx configuration..."
nginx -t

# Setup firewall
print_status "Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "y" | ufw enable

# Create logrotate config
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/scan2talk << 'EOF'
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
EOF

echo ""
echo "=========================================="
print_status "Initial setup completed!"
echo "=========================================="
echo ""
print_warning "NEXT STEPS:"
echo "1. Edit /var/www/scan2talk/.env with your actual values"
echo "2. Generate SECRET_KEY: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo "3. Update ALLOWED_HOSTS with your domain"
echo "4. Run migrations: cd /var/www/scan2talk && source venv/bin/activate && python manage.py migrate"
echo "5. Create superuser: python manage.py createsuperuser"
echo "6. Collect static: python manage.py collectstatic --noinput"
echo "7. Start services: systemctl start gunicorn && systemctl enable gunicorn"
echo "8. Restart Nginx: systemctl restart nginx"
echo "9. Setup SSL: certbot --nginx -d your-domain.com"
echo ""
print_status "Your server is ready for deployment!"
