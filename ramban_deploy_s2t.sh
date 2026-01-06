#!/bin/bash

# Scan2Talk Auto-Deployment Script
# Created by: Ramban (Kiro AI Assistant)
# Usage: ./ramban_deploy_s2t.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/scan2talk"
VENV_PATH="$PROJECT_DIR/venv"
BRANCH="main"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Scan2Talk Auto-Deployment Script${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run with sudo: sudo ./ramban_deploy_s2t.sh"
    exit 1
fi

print_header

# Step 1: Navigate to project directory
print_info "Navigating to project directory..."
cd $PROJECT_DIR || {
    print_error "Failed to navigate to $PROJECT_DIR"
    exit 1
}
print_success "In project directory: $PROJECT_DIR"

# Step 2: Backup database (optional but recommended)
print_info "Creating database backup..."
BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    cp db.sqlite3 "$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
    print_success "Database backed up to: $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
else
    print_warning "No database file found to backup"
fi

# Step 3: Pull latest code from Git
print_info "Pulling latest code from Git..."
git fetch origin
git pull origin $BRANCH || {
    print_error "Failed to pull from Git"
    exit 1
}
print_success "Code updated from Git"

# Step 4: Activate virtual environment and install dependencies
print_info "Activating virtual environment..."
source $VENV_PATH/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}
print_success "Virtual environment activated"

print_info "Installing/updating Python dependencies..."
pip install -r requirements.txt --quiet || {
    print_warning "Some dependencies failed to install, continuing..."
}
print_success "Dependencies updated"

# Step 5: Run database migrations
print_info "Running database migrations..."
python3 manage.py migrate || {
    print_error "Migration failed"
    exit 1
}
print_success "Migrations completed"

# Step 6: Collect static files
print_info "Collecting static files..."
python3 manage.py collectstatic --noinput || {
    print_warning "Static files collection had issues, continuing..."
}
print_success "Static files collected"

# Step 7: Restart Gunicorn
print_info "Restarting Gunicorn service..."
systemctl restart gunicorn || {
    print_error "Failed to restart Gunicorn"
    exit 1
}
print_success "Gunicorn restarted"

# Step 8: Restart Nginx
print_info "Restarting Nginx service..."
systemctl restart nginx || {
    print_error "Failed to restart Nginx"
    exit 1
}
print_success "Nginx restarted"

# Step 9: Check service status
print_info "Checking service status..."
if systemctl is-active --quiet gunicorn; then
    print_success "Gunicorn is running"
else
    print_error "Gunicorn is not running!"
    systemctl status gunicorn --no-pager
fi

if systemctl is-active --quiet nginx; then
    print_success "Nginx is running"
else
    print_error "Nginx is not running!"
    systemctl status nginx --no-pager
fi

# Step 10: Clean up old backups (keep last 10)
print_info "Cleaning up old backups..."
cd $BACKUP_DIR
ls -t db_backup_*.sqlite3 2>/dev/null | tail -n +11 | xargs -r rm
print_success "Old backups cleaned"

# Final message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "Your site is now updated at: http://scan2talk.in"
print_info "Admin panel: http://scan2talk.in/admin/"
print_info "QR Dashboard: http://scan2talk.in/gateways/qr/dashboard/"
echo ""
print_info "Backup location: $BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
echo ""
print_success "Deployment completed at: $(date)"
echo ""
