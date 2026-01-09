#!/bin/bash

# Quick fix for deployment conflict
# Run this on your SSH server: sudo bash fix_deployment_conflict.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info(){ echo -e "${BLUE}ℹ${NC} $1"; }
ok(){ echo -e "${GREEN}✓${NC} $1"; }
warn(){ echo -e "${YELLOW}⚠${NC} $1"; }
fail(){ echo -e "${RED}✗${NC} $1"; exit 1; }

PROJECT_DIR="/var/www/scan2talk"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Fix Deployment Conflict${NC}"
echo -e "${BLUE}========================================${NC}"

info "Moving to project directory"
cd "$PROJECT_DIR" || fail "Project dir not found"

info "Checking git status"
git status

info "Stashing local changes"
git stash push -m "Fix deployment conflict $(date +%Y%m%d_%H%M%S)"
ok "Local changes stashed"

info "Pulling latest code"
git pull origin main
ok "Code updated"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CONFLICT RESOLVED${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
info "You can now run: sudo bash ramban_deploy_s2t.sh"
echo ""
