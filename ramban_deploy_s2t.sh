#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/var/www/scan2talk"
VENV_PATH="/var/www/venv"
PYTHON_BIN="/usr/bin/python3.12"
BRANCH="main"

# ===== PostgreSQL Config =====
DB_NAME="scan2talk_db"
DB_USER="postgres"
DB_HOST="127.0.0.1"
BACKUP_DIR="$PROJECT_DIR/backups"

info(){ echo -e "${BLUE}ℹ${NC} $1"; }
ok(){ echo -e "${GREEN}✓${NC} $1"; }
warn(){ echo -e "${YELLOW}⚠${NC} $1"; }
fail(){ echo -e "${RED}✗${NC} $1"; exit 1; }

[ "$EUID" -eq 0 ] || fail "Run with sudo"

echo -e "${BLUE}Scan2Talk Production Deployment (Postgres Mode)${NC}"

cd "$PROJECT_DIR" || fail "Project directory not found"

# ===== Step 1: Backup PostgreSQL =====
info "Backing up PostgreSQL database"
mkdir -p "$BACKUP_DIR"
TS=$(date +%Y%m%d_%H%M%S)

pg_dump -U "$DB_USER" -h "$DB_HOST" "$DB_NAME" > "$BACKUP_DIR/db_backup_$TS.sql" \
  && ok "Postgres backup created" \
  || warn "Postgres backup failed"

# ===== Step 2: Git Update =====
info "Updating code"
git fetch origin
if ! git diff-index --quiet HEAD --; then
  warn "Local changes detected, stashing"
  git stash push -m "Auto-stash $(date +%F_%T)"
fi
git pull origin "$BRANCH"
ok "Code updated"

# ===== Step 3: Recreate venv =====
info "Recreating virtualenv"
rm -rf "$VENV_PATH"
"$PYTHON_BIN" -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
ok "Fresh virtualenv activated"

# ===== Step 4: Upgrade pip =====
info "Bootstrapping pip"
python -m ensurepip --upgrade
pip install --upgrade pip setuptools wheel
ok "pip ready"

# ===== Step 5: Install Dependencies =====
info "Installing dependencies"
pip install --only-binary=:all: "numpy>=1.26.4"
pip install --only-binary=:all: -r requirements.txt
ok "Dependencies installed"

# ===== Step 6: Django Ops =====
info "Running migrations"
python manage.py migrate
ok "Migrations complete"

info "Collecting static"
python manage.py collectstatic --noinput
ok "Static collected"

# ===== Step 7: Restart Services =====
info "Restarting Gunicorn"
systemctl restart gunicorn
ok "Gunicorn restarted"

info "Restarting Nginx"
systemctl restart nginx
ok "Nginx restarted"

# ===== Step 8: Health Check =====
systemctl is-active --quiet gunicorn || fail "Gunicorn down"
systemctl is-active --quiet nginx || fail "Nginx down"
ok "Services healthy"

# ===== Step 9: Cleanup Old Backups =====
info "Cleaning old Postgres backups"
cd "$BACKUP_DIR"
ls -t db_backup_*.sql | tail -n +11 | xargs -r rm
ok "Old backups cleaned"

echo ""
ok "DEPLOYMENT SUCCESSFUL"
info "Site: https://scan2talk.in"
info "Admin: https://scan2talk.in/admin"
info "DB Backup: $BACKUP_DIR/db_backup_$TS.sql"
echo ""
