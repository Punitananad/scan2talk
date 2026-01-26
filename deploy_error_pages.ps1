# Deploy Error Pages Fix to Production
# This script deploys custom error handlers and templates

Write-Host "🚀 Deploying Error Pages Fix to Production..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check git status
Write-Host "📋 Checking git status..." -ForegroundColor Yellow
git status

# Add changes
Write-Host "📦 Adding changes to git..." -ForegroundColor Yellow
git add apps/core/error_handlers.py
git add templates/errors/
git add gateway_platform/urls.py
git add templates/gateways/gateway_detail.html
git add apps/gateways/views.py

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Add custom error handlers and templates for production

- Created custom 404, 500, 403, 400 error pages
- Added error_handlers.py with custom error views
- Updated urls.py to use custom error handlers
- Fixed gateway detail view template issue
- Prevents exposure of URL patterns in production"

# Push to repository
Write-Host "🔄 Pushing to repository..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ Changes pushed to repository!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📝 NEXT STEPS ON PRODUCTION SERVER:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SSH into your production server:"
Write-Host "   ssh root@68.183.91.15"
Write-Host ""
Write-Host "2. Navigate to project directory:"
Write-Host "   cd /root/CPA"
Write-Host ""
Write-Host "3. Pull the latest changes:"
Write-Host "   git pull origin main"
Write-Host ""
Write-Host "4. Collect static files:"
Write-Host "   python manage.py collectstatic --noinput"
Write-Host ""
Write-Host "5. Restart the application:"
Write-Host "   systemctl restart gunicorn"
Write-Host "   systemctl restart nginx"
Write-Host ""
Write-Host "6. Check the status:"
Write-Host "   systemctl status gunicorn"
Write-Host ""
Write-Host "7. Test the error pages:"
Write-Host "   Visit: https://scan2talk.in/nonexistent-page"
Write-Host ""
Write-Host "✅ Deployment script completed!" -ForegroundColor Green
