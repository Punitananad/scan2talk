#!/bin/bash

# Deployment script for landing page speed optimization
# Run this on the production server at /var/www/scan2talk

echo "=========================================="
echo "Deploying Landing Page Speed Optimization"
echo "=========================================="

# Navigate to project directory
cd /var/www/scan2talk || exit 1

# Pull latest changes
echo "Pulling latest code from GitHub..."
git pull origin main

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Restart Gunicorn
echo "Restarting Gunicorn..."
systemctl restart gunicorn

# Restart Nginx
echo "Restarting Nginx..."
systemctl restart nginx

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Changes applied:"
echo "✓ Removed Swiper slider library (replaced with static image)"
echo "✓ Removed AOS animation library"
echo "✓ Removed all animation attributes from HTML"
echo "✓ Significantly reduced page load time"
echo ""
echo "Test the landing page at your domain to verify speed improvements."
