#!/bin/bash

# Scan2Talk Auto-Deployment Script
# Created by: Ramban (Kiro AI Assistant)
# Hardened by: ChatGPT (production-safe)
# Usage: sudo bash ramban_deploy_s2t.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config
PROJECT_DIR="/var/www/scan2talk"
VENV_PATH="/var/www/venv"  # Virtual environment is outside project directory
BRANCH="main"

# Helpers
info(){ echo -e "${BLUE}ℹ${NC} $1"; }
ok(){ echo -e "${GREEN}✓${NC} $1"; }
warn(){ echo -e "${YELLOW}⚠${NC} $1"; }
fail(){ echo -e "${RED}✗${NC} $1"; exit 1; }

# Root check
if [ "$EUID" -ne 0 ]; then
  fail "Run with sudo: sudo bash ramban_deploy_s2t.sh"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Scan2Talk Production Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Step 1: cd
info "Moving to project directory"
cd "$PROJECT_DIR" || fail "Project dir not found"

# Step 2: DB backup
info "Backing up database"
mkdir -p backups
TS=$(date +%Y%m%d_%H%M%S)
if [ -f db.sqlite3 ]; then
  cp db.sqlite3 "backups/db_backup_$TS.sqlite3"
  ok "DB backup created"
else
  warn "No sqlite DB found (skipping backup)"
fi

# Step 3: Git pull (with stash for local changes)
info "Pulling latest code"
git fetch origin

# Check for local changes
if ! git diff-index --quiet HEAD --; then
  warn "Local changes detected, stashing..."
  git stash push -m "Auto-stash before deployment $(date +%Y%m%d_%H%M%S)"
  ok "Local changes stashed"
fi

git pull origin "$BRANCH"
ok "Code updated"

# Step 4: Virtualenv (AUTO-FIX)
if [ ! -d "$VENV_PATH" ]; then
  warn "Virtualenv missing. Creating venv..."
  python3 -m venv "$VENV_PATH"
  ok "Virtualenv created"
fi

if [ ! -f "$VENV_PATH/bin/activate" ]; then
  fail "venv exists but activate script missing"
fi

info "Activating virtualenv"
source "$VENV_PATH/bin/activate"
ok "Virtualenv active"

# Step 5: Dependencies
info "Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt
ok "Dependencies installed"

# Step 6: Migrations
info "Running migrations"
python manage.py migrate
ok "Migrations done"

# Step 7: Static files
info "Collecting static files"
python manage.py collectstatic --noinput || warn "Static warnings ignored"
ok "Static collected"

# Step 8: Restart services
info "Restarting Gunicorn"
systemctl restart gunicorn
ok "Gunicorn restarted"

info "Restarting Nginx"
systemctl restart nginx
ok "Nginx restarted"

# Step 9: Health check
systemctl is-active --quiet gunicorn && ok "Gunicorn running" || fail "Gunicorn down"
systemctl is-active --quiet nginx && ok "Nginx running" || fail "Nginx down"

# Step 10: Cleanup backups (keep 10)
info "Cleaning old backups"
cd backups
ls -t db_backup_*.sqlite3 2>/dev/null | tail -n +11 | xargs -r rm
ok "Old backups cleaned"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOYMENT SUCCESSFUL${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
info "Site: http://scan2talk.in"
info "Admin: http://scan2talk.in/admin/"
info "QR Dashboard: http://scan2talk.in/gateways/qr/dashboard/"
info "Backup: backups/db_backup_$TS.sqlite3"
echo ""
ok "Completed at $(date)"
