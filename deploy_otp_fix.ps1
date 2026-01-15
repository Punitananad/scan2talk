# PowerShell script to deploy OTP verification fix to production
# Run this from your Windows machine

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OTP Verification Fix Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration - UPDATE THESE
$SERVER_USER = "root"  # Your SSH user
$SERVER_HOST = "your-server-ip"  # Your server IP or domain
$PROJECT_PATH = "/root/gateway_platform"  # Path to your Django project

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Server: $SERVER_USER@$SERVER_HOST" -ForegroundColor White
Write-Host "  Project: $PROJECT_PATH" -ForegroundColor White
Write-Host ""

# Step 1: Commit and push changes
Write-Host "Step 1: Committing changes to Git..." -ForegroundColor Green
git add apps/gateways/qr_views.py requirements.txt OTP_VERIFICATION_FIX.md test_otp_verification_fix.py
git commit -m "Fix: OTP verification session persistence + add numpy/reportlab for PDF generation"
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git push failed. Fix the error and try again." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Changes pushed to Git" -ForegroundColor Green
Write-Host ""

# Step 2: Deploy to server
Write-Host "Step 2: Deploying to production server..." -ForegroundColor Green
Write-Host ""

$DEPLOY_COMMANDS = @"
cd $PROJECT_PATH && \
echo '📥 Pulling latest code...' && \
git pull origin main && \
echo '📦 Installing dependencies...' && \
source venv/bin/activate && \
pip install -r requirements.txt && \
echo '🔄 Restarting server...' && \
sudo systemctl restart gunicorn && \
echo '✅ Deployment complete!' && \
echo '' && \
echo '📊 Checking server status...' && \
sudo systemctl status gunicorn --no-pager -l
"@

Write-Host "Connecting to server and deploying..." -ForegroundColor Yellow
ssh "$SERVER_USER@$SERVER_HOST" $DEPLOY_COMMANDS

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed. Check the error above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT SUCCESSFUL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test OTP flow: Go to /gateways/activate/<QR_CODE>/" -ForegroundColor White
Write-Host "2. Check logs: ssh $SERVER_USER@$SERVER_HOST 'tail -f /var/log/gunicorn/error.log'" -ForegroundColor White
Write-Host "3. Test PDF generation: Generate a batch with 'Download PDF' option" -ForegroundColor White
Write-Host ""
Write-Host "Debug Commands:" -ForegroundColor Yellow
Write-Host "  View logs: ssh $SERVER_USER@$SERVER_HOST 'sudo journalctl -u gunicorn -f'" -ForegroundColor White
Write-Host "  Restart: ssh $SERVER_USER@$SERVER_HOST 'sudo systemctl restart gunicorn'" -ForegroundColor White
Write-Host ""
