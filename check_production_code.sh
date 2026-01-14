#!/bin/bash

echo "======================================================================"
echo "🔍 CHECKING PRODUCTION CODE STATUS"
echo "======================================================================"

echo ""
echo "1️⃣  Checking OTP Service File..."
echo "----------------------------------------------------------------------"

if grep -q "Accounts/{self.auth_key}" apps/communications/otp_service.py; then
    echo "✅ NEW CODE FOUND - Account-scoped endpoint is present"
else
    echo "❌ OLD CODE DETECTED - Still using wrong endpoint"
    echo ""
    echo "🚨 ACTION REQUIRED:"
    echo "   git pull origin main"
    echo "   sudo systemctl restart gunicorn"
fi

echo ""
echo "2️⃣  Checking Current Endpoint..."
echo "----------------------------------------------------------------------"
grep -A 2 "self.api_endpoint" apps/communications/otp_service.py | head -5

echo ""
echo "3️⃣  Checking Response Validation..."
echo "----------------------------------------------------------------------"
if grep -q 'response_data.get("Success")' apps/communications/otp_service.py; then
    echo "✅ NEW CODE - Checking Success field in response"
else
    echo "❌ OLD CODE - Not checking Success field"
fi

echo ""
echo "4️⃣  Checking Git Status..."
echo "----------------------------------------------------------------------"
git log -1 --oneline
echo ""
git status --short

echo ""
echo "5️⃣  Checking if Server Needs Restart..."
echo "----------------------------------------------------------------------"
if systemctl is-active --quiet gunicorn; then
    echo "Gunicorn is running"
    echo "Last restart: $(systemctl show gunicorn -p ActiveEnterTimestamp --value)"
    echo ""
    echo "⚠️  If code was updated, restart with:"
    echo "   sudo systemctl restart gunicorn"
elif supervisorctl status | grep -q "RUNNING"; then
    echo "Supervisor is running"
    echo ""
    echo "⚠️  If code was updated, restart with:"
    echo "   sudo supervisorctl restart all"
else
    echo "⚠️  Could not detect process manager"
    echo "   Manually restart your Django server"
fi

echo ""
echo "======================================================================"
echo "✅ CHECK COMPLETE"
echo "======================================================================"
