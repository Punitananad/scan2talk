#!/bin/bash
# Razorpay Deployment Script for Linux/Mac
# This script deploys Razorpay payment gateway to production

echo "========================================"
echo "  Razorpay Payment Gateway Deployment  "
echo "========================================"
echo ""

# Step 1: Git Status
echo "[1/5] Checking Git Status..."
git status

echo ""
read -p "Continue with deployment? (y/n): " continue
if [ "$continue" != "y" ]; then
    echo "Deployment cancelled."
    exit 1
fi

# Step 2: Add and Commit Changes
echo ""
echo "[2/5] Committing Changes..."
git add .
git commit -m "Add Razorpay payment gateway integration"

# Step 3: Push to Repository
echo ""
echo "[3/5] Pushing to Repository..."
git push origin main

if [ $? -ne 0 ]; then
    echo "Git push failed. Please check your connection and try again."
    exit 1
fi

# Step 4: Deploy to Production Server
echo ""
echo "[4/5] Deploying to Production Server..."
echo "Server: 68.183.91.15"

ssh root@68.183.91.15 << 'EOF'
cd /root/CPA && \
git pull origin main && \
echo '✅ Code pulled successfully' && \
sudo systemctl restart gunicorn && \
echo '✅ Gunicorn restarted' && \
sudo systemctl restart nginx && \
echo '✅ Nginx restarted' && \
echo '' && \
echo '========================================' && \
echo '  Deployment Complete!' && \
echo '========================================' && \
echo '' && \
echo 'Next Steps:' && \
echo '1. Configure Razorpay webhook in dashboard' && \
echo '2. Test recharge flow at https://scan2talk.in/accounts/wallet/recharge/' && \
echo '3. Monitor logs: tail -f /var/log/gunicorn/error.log'
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "Deployment failed. Please check server connection."
    exit 1
fi

# Step 5: Summary
echo ""
echo "========================================"
echo "  Deployment Successful! ✅"
echo "========================================"
echo ""
echo "Razorpay Configuration:"
echo "  Key ID: rzp_live_iBh2Pp5ymtg0RS"
echo "  Webhook URL: https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/"
echo "  Webhook Secret: scan2talk_rzp_webhook_live_2026"
echo ""
echo "Next Steps:"
echo "  1. Configure webhook in Razorpay Dashboard"
echo "     URL: https://dashboard.razorpay.com/app/webhooks"
echo ""
echo "  2. Test the payment flow"
echo "     URL: https://scan2talk.in/accounts/wallet/recharge/"
echo ""
echo "  3. Monitor server logs"
echo "     Command: ssh root@68.183.91.15 'tail -f /var/log/gunicorn/error.log'"
echo ""
echo "Documentation: RAZORPAY_DEPLOYMENT_GUIDE.md"
echo ""
