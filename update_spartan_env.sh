#!/bin/bash
# Update Spartan credentials in production .env file

echo "🔧 Updating Spartan credentials in production..."

# SSH into production server and update .env
ssh ramban@103.127.29.78 << 'ENDSSH'
cd /home/ramban/gateway_platform

# Backup current .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Update Spartan credentials
sed -i 's/^SPARKTG_USERNAME=.*/SPARKTG_USERNAME=10215500/' .env
sed -i 's/^SPARKTG_PASSWORD=.*/SPARKTG_PASSWORD=Admin@007/' .env
sed -i 's/^SPARKTG_SID=.*/SPARKTG_SID=2155/' .env

# Add or update DID number
if grep -q "^SPARKTG_DID_NUMBER=" .env; then
    sed -i 's/^SPARKTG_DID_NUMBER=.*/SPARKTG_DID_NUMBER=01205018960/' .env
else
    echo "SPARKTG_DID_NUMBER=01205018960" >> .env
fi

echo "✅ Spartan credentials updated"

# Show updated values (masked password)
echo ""
echo "📋 Updated credentials:"
grep "^SPARKTG_" .env | sed 's/\(SPARKTG_PASSWORD=\).*/\1***HIDDEN***/'

# Restart services
echo ""
echo "🔄 Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Services restarted"
echo ""
echo "🎉 Spartan credentials updated successfully!"

ENDSSH

echo ""
echo "✅ Done! Production server updated."
