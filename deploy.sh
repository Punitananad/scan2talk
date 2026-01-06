#!/bin/bash

# Scan2Talk Deployment Script
# Run this on your Ubuntu server after initial setup

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/scan2talk"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/Punitananad/scan2talk.git"

# Function to print colored output
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
if [ "$EUID" -eq 0 ]; then 
    print_error "Please don't run as root. Run as regular user with sudo privileges."
    exit 1
fi

# Update code from git
print_status "Pulling latest code from GitHub..."
cd $PROJECT_DIR
git pull origin main

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt --quiet

# Run migrations
print_status "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create necessary directories
print_status "Creating required directories..."
mkdir -p logs media/qr_codes

# Set permissions
print_status "Setting permissions..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

# Restart services
print_status "Restarting Gunicorn..."
sudo systemctl restart gunicorn

print_status "Restarting Nginx..."
sudo systemctl restart nginx

# Check service status
if sudo systemctl is-active --quiet gunicorn; then
    print_status "Gunicorn is running"
else
    print_error "Gunicorn failed to start!"
    sudo journalctl -u gunicorn -n 20
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx failed to start!"
    sudo journalctl -u nginx -n 20
    exit 1
fi

echo ""
print_status "🎉 Deployment completed successfully!"
echo ""
echo "Your application is now live!"
echo "Check logs with: sudo journalctl -u gunicorn -f"
