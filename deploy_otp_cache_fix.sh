#!/bin/bash

# Deploy OTP Cache Fix - Critical Multi-Worker Issue
# This fixes "OTP expired or not found" errors

set -e

echo "=================================================="
echo "🚀 DEPLOYING OTP CACHE FIX"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Create cache directory
echo -e "${YELLOW}📁 Creating cache directory...${NC}"
sudo mkdir -p /var/tmp/django_cache
sudo chmod 777 /var/tmp/django_cache
echo -e "${GREEN}✓ Cache directory created${NC}"
echo ""

# 2. Pull latest code
echo -e "${YELLOW}📥 Pulling latest code...${NC}"
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# 3. Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python3 manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

# 4. Clear old cache
echo -e "${YELLOW}🧹 Clearing old cache...${NC}"
python3 manage.py shell -c "from django.core.cache import cache; cache.clear(); print('Cache cleared')"
echo -e "${GREEN}✓ Cache cleared${NC}"
echo ""

# 5. Restart Gunicorn
echo -e "${YELLOW}🔄 Restarting Gunicorn...${NC}"
sudo systemctl restart gunicorn
sleep 2
echo -e "${GREEN}✓ Gunicorn restarted${NC}"
echo ""

# 6. Restart Nginx
echo -e "${YELLOW}🔄 Restarting Nginx...${NC}"
sudo systemctl restart nginx
sleep 1
echo -e "${GREEN}✓ Nginx restarted${NC}"
echo ""

# 7. Check services
echo -e "${YELLOW}🔍 Checking services...${NC}"
if systemctl is-active --quiet gunicorn; then
    echo -e "${GREEN}✓ Gunicorn is running${NC}"
else
    echo -e "${RED}✗ Gunicorn is NOT running${NC}"
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx is NOT running${NC}"
    exit 1
fi
echo ""

# 8. Check Gunicorn workers
echo -e "${YELLOW}👷 Checking Gunicorn workers...${NC}"
WORKER_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
echo -e "${GREEN}✓ $WORKER_COUNT Gunicorn workers running${NC}"
echo ""

# 9. Verify cache directory
echo -e "${YELLOW}📂 Verifying cache directory...${NC}"
ls -lh /var/tmp/django_cache/ | head -5
echo -e "${GREEN}✓ Cache directory accessible${NC}"
echo ""

# 10. Test cache
echo -e "${YELLOW}🧪 Testing cache...${NC}"
python3 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
result = cache.get('test_key')
if result == 'test_value':
    print('✓ Cache is working correctly')
else:
    print('✗ Cache test failed')
    exit(1)
"
echo ""

echo "=================================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "=================================================="
echo ""
echo "🎯 What was fixed:"
echo "   - Changed from LocMemCache to FileBasedCache"
echo "   - OTP now shared across all Gunicorn workers"
echo "   - No more 'OTP expired or not found' errors"
echo ""
echo "🧪 Test now:"
echo "   1. Scan a QR code"
echo "   2. Enter phone number"
echo "   3. Enter OTP on FIRST attempt"
echo "   4. Should verify successfully!"
echo ""
echo "📊 Monitor logs:"
echo "   tail -f /var/log/gunicorn/error.log | grep OTP"
echo ""
echo "🌐 Site: https://scan2talk.in"
echo ""
