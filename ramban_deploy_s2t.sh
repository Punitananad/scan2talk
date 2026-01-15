#!/bin/bash
# Scan2Talk Production Deployment Script (Hardened)
# Python 3.12 + Binary-only deps + Clean venv
# Usage: sudo bash ramban_deploy_s2t.sh

set -e

# ===== Colors =====
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== Config =====
PROJECT_DIR="/var/www/scan2talk"
VENV_PATH="/var/www/venv"
PYTHON_BIN="/usr/bin/python3.12"
BRANCH="main"

# ===== Helpers =====
info(){ echo -e "${BLUE}ℹ${NC} $1"; }
ok(){ echo -e "${GREEN}✓${NC} $1"; }
warn(){ echo -e "${YELLOW}⚠${NC} $1"; }
fail(){ echo -e "${RED}✗${NC} $1"; exit 1; }

# ===== Root check =====
[ "$EUID" -eq 0 ] || fail "Run with sudo"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Scan2Talk Production Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# ===== Step 1: Project dir =====
info "Moving to project directory"
cd "$PROJECT_DIR" || fail "Project directory not found"

# ===== Step 2: DB backup =====
info "Backing up database"
mkdir -p backups
TS=$(date +%Y%m%d_%H%M%S)
[ -f db.sqlite3 ] && cp db.sqlite3 "backups/db_backup_$TS.sqlite3" && ok "DB backup created" || warn "No DB found"

# ===== Step 3: Git pull (safe) =====
info "Updating code"
git fetch origin
if ! git diff-index --quiet HEAD --; then
  warn "Local changes detected, stashing"
  git stash push -m "Auto-stash $(date +%F_%T)"
fi
git pull origin "$BRANCH"
ok "Code updated"

# ===== Step 4: Recreate venv (CLEAN) =====
info "Recreating virtualenv"
rm -rf "$VENV_PATH"
"$PYTHON_BIN" -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
ok "Fresh virtualenv activated"

# ===== Step 5: Bootstrap toolchain =====
info "Bootstrapping pip toolchain"
python -m ensurepip --upgrade
pip install --upgrade pip setuptools wheel
ok "pip / setuptools / wheel ready"

# ===== Step 6: Install deps (binary-only) =====
info "Installing dependencies (binary-only)"
pip install --only-binary=:all: "numpy>=1.26.4"
pip install --only-binary=:all: -r requirements.txt
ok "Dependencies installed"

# ===== Step 7: Django ops =====
info "Running migrations"
python manage.py migrate
ok "Migrations complete"

info "Collecting static files"
python manage.py collectstatic --noinput
ok "Static collected"

# ===== Step 8: Restart services =====
info "Restarting Gunicorn"
systemctl restart gunicorn
ok "Gunicorn restarted"

info "Restarting Nginx"
systemctl restart nginx
ok "Nginx restarted"

# ===== Step 9: Health check =====
systemctl is-active --quiet gunicorn || fail "Gunicorn down"
systemctl is-active --quiet nginx || fail "Nginx down"
ok "Services healthy"

# ===== Step 10: Cleanup old backups =====
info "Cleaning old DB backups"
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
ok "Completed at $(date)"
