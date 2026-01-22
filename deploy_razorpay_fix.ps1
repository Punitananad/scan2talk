# Deploy Razorpay configuration fix to production server
# PowerShell script for Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Razorpay Configuration Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with Razorpay credentials"
    exit 1
}

# Check if Razorpay credentials are in .env
$envContent = Get-Content .env -Raw

if ($envContent -notmatch "RAZORPAY_KEY_ID") {
    Write-Host "✗ RAZORPAY_KEY_ID not found in .env" -ForegroundColor Red
    Write-Host "Please add: RAZORPAY_KEY_ID=rzp_live_iBh2Pp5ymtg0RS"
    exit 1
}

if ($envContent -notmatch "RAZORPAY_KEY_SECRET") {
    Write-Host "✗ RAZORPAY_KEY_SECRET not found in .env" -ForegroundColor Red
    Write-Host "Please add: RAZORPAY_KEY_SECRET=kaFVBMGJHj5GhXIoFH34WgsO"
    exit 1
}

Write-Host "✓ .env file found with Razorpay credentials" -ForegroundColor Green

# Run diagnostic check
Write-Host ""
Write-Host "Running diagnostic check..." -ForegroundColor Yellow
python check_razorpay_config.py

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS FOR PRODUCTION SERVER:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Upload .env file to production server" -ForegroundColor Yellow
Write-Host "2. SSH into production server" -ForegroundColor Yellow
Write-Host "3. Run: python check_razorpay_config.py" -ForegroundColor Yellow
Write-Host "4. Restart Django application:" -ForegroundColor Yellow
Write-Host "   - sudo systemctl restart gunicorn" -ForegroundColor White
Write-Host "   - OR: sudo systemctl restart uwsgi" -ForegroundColor White
Write-Host "5. Test at: https://scan2talk.in/order-tag/" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
