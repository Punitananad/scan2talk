#!/bin/bash

# Deploy Error Pages Fix to Production
# This script deploys custom error handlers and templates

echo "🚀 Deploying Error Pages Fix to Production..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're on the right branch
echo -e "${YELLOW}📋 Checking git status...${NC}"
git status

# Add changes
echo -e "${YELLOW}📦 Adding changes to git...${NC}"
git add apps/core/error_handlers.py
git add templates/errors/
git add gateway_platform/urls.py
git add templates/gateways/gateway_detail.html
git add apps/gateways/views.py

# Commit changes
echo -e "${YELLOW}💾 Committing changes...${NC}"
git commit -m "Add custom error handlers and templates for production

- Created custom 404, 500, 403, 400 error pages
- Added error_handlers.py with custom error views
- Updated urls.py to use custom error handlers
- Fixed gateway detail view template issue
- Prevents exposure of URL patterns in production"

# Push to repository
echo -e "${YELLOW}🔄 Pushing to repository...${NC}"
git push origin main

echo ""
echo -e "${GREEN}✅ Changes pushed to repository!${NC}"
echo ""
echo "================================================"
echo "📝 NEXT STEPS ON PRODUCTION SERVER:"
echo "================================================"
echo ""
echo "1. SSH into your production server:"
echo "   ssh root@68.183.91.15"
echo ""
echo "2. Navigate to project directory:"
echo "   cd /root/CPA"
echo ""
echo "3. Pull the latest changes:"
echo "   git pull origin main"
echo ""
echo "4. Collect static files:"
echo "   python manage.py collectstatic --noinput"
echo ""
echo "5. Restart the application:"
echo "   systemctl restart gunicorn"
echo "   systemctl restart nginx"
echo ""
echo "6. Check the status:"
echo "   systemctl status gunicorn"
echo ""
echo "7. Test the error pages:"
echo "   Visit: https://scan2talk.in/nonexistent-page"
echo ""
echo -e "${GREEN}✅ Deployment script completed!${NC}"
