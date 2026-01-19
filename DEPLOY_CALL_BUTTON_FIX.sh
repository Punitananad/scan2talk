#!/bin/bash
# Deploy Call Button Fix to Production

echo "🚀 Deploying Call Button Fix..."

# Add and commit changes
git add templates/core/gateway_access.html
git commit -m "Fix: Make call owner button directly clickable - initiates call immediately"

# Push to repository
git push origin main

echo "✅ Pushed to repository"

# Deploy to production server
echo "📡 Deploying to production server..."

ssh ramban@103.127.29.78 << 'ENDSSH'
cd /home/ramban/gateway_platform

echo "📥 Pulling latest changes..."
git pull origin main

echo "🔄 Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Services restarted"

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status gunicorn --no-pager | head -n 5
sudo systemctl status nginx --no-pager | head -n 5

echo ""
echo "🎉 Deployment complete!"
echo "🔗 Test at: https://scan2talk.in/gateways/g/YOUR_QR_CODE/"

ENDSSH

echo ""
echo "✅ Call button fix deployed successfully!"
echo ""
echo "📝 What was fixed:"
echo "  - Call button now directly initiates calls"
echo "  - Removed confusing two-step process"
echo "  - Better user experience"
echo ""
echo "🧪 Test the fix:"
echo "  1. Visit: https://scan2talk.in/gateways/g/ABC123/"
echo "  2. Click 'Call Owner' button"
echo "  3. Should show loading and redirect to dialer"
