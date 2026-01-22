# Razorpay Deployment Script for Windows PowerShell
# This script deploys Razorpay payment gateway to production

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Razorpay Payment Gateway Deployment  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Git Status
Write-Host "[1/5] Checking Git Status..." -ForegroundColor Yellow
git status

Write-Host ""
$continue = Read-Host "Continue with deployment? (y/n)"
if ($continue -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Red
    exit
}

# Step 2: Add and Commit Changes
Write-Host ""
Write-Host "[2/5] Committing Changes..." -ForegroundColor Yellow
git add .
git commit -m "Add Razorpay payment gateway integration"

# Step 3: Push to Repository
Write-Host ""
Write-Host "[3/5] Pushing to Repository..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git push failed. Please check your connection and try again." -ForegroundColor Red
    exit
}

# Step 4: Deploy to Production Server
Write-Host ""
Write-Host "[4/5] Deploying to Production Server..." -ForegroundColor Yellow
Write-Host "Server: 68.183.91.15" -ForegroundColor Cyan

$deployCommands = @"
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
"@

ssh root@68.183.91.15 $deployCommands

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Deployment failed. Please check server connection." -ForegroundColor Red
    exit
}

# Step 5: Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Successful! ✅" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Razorpay Configuration:" -ForegroundColor Cyan
Write-Host "  Key ID: rzp_live_iBh2Pp5ymtg0RS" -ForegroundColor White
Write-Host "  Webhook URL: https://scan2talk.in/api/v1/auth/wallet/razorpay/webhook/" -ForegroundColor White
Write-Host "  Webhook Secret: scan2talk_rzp_webhook_live_2026" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Configure webhook in Razorpay Dashboard" -ForegroundColor White
Write-Host "     URL: https://dashboard.razorpay.com/app/webhooks" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Test the payment flow" -ForegroundColor White
Write-Host "     URL: https://scan2talk.in/accounts/wallet/recharge/" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Monitor server logs" -ForegroundColor White
Write-Host "     Command: ssh root@68.183.91.15 'tail -f /var/log/gunicorn/error.log'" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation: RAZORPAY_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
