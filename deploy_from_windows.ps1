# Windows PowerShell Deployment Helper
# This script helps you deploy to the production server from Windows

Write-Host "==================================" -ForegroundColor Blue
Write-Host "  Scan2Talk Deployment Helper" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host ""

$SERVER_IP = "68.183.91.15"
$SERVER_USER = "root"
$PROJECT_DIR = "/var/www/scan2talk"

Write-Host "This script will connect to: $SERVER_USER@$SERVER_IP" -ForegroundColor Yellow
Write-Host ""
Write-Host "You will need to enter your SSH password when prompted." -ForegroundColor Yellow
Write-Host ""

# Create the deployment command
$DEPLOY_COMMAND = @"
cd $PROJECT_DIR && \
echo '=== Starting Deployment ===' && \
mkdir -p backups && \
cp db.sqlite3 backups/db_backup_`$(date +%Y%m%d_%H%M%S).sqlite3 2>/dev/null || echo 'No DB to backup' && \
echo '=== Pulling latest code ===' && \
git stash && \
git pull origin main && \
echo '=== Activating virtualenv ===' && \
source /var/www/venv/bin/activate && \
echo '=== Installing dependencies ===' && \
pip install -r requirements.txt && \
echo '=== Running migrations ===' && \
python manage.py migrate && \
echo '=== Collecting static files ===' && \
python manage.py collectstatic --noinput && \
echo '=== Restarting services ===' && \
systemctl restart gunicorn && \
systemctl restart nginx && \
echo '=== Checking service status ===' && \
systemctl is-active gunicorn && \
systemctl is-active nginx && \
echo '=== DEPLOYMENT COMPLETE ===' && \
echo 'Site: http://scan2talk.in' && \
echo 'Admin: http://scan2talk.in/admin/'
"@

Write-Host "Connecting to server and running deployment..." -ForegroundColor Green
Write-Host ""

# Execute SSH command
ssh "$SERVER_USER@$SERVER_IP" $DEPLOY_COMMAND

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Red
    Write-Host "  DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try connecting manually:" -ForegroundColor Yellow
    Write-Host "  ssh $SERVER_USER@$SERVER_IP" -ForegroundColor Cyan
    Write-Host "  cd $PROJECT_DIR" -ForegroundColor Cyan
    Write-Host "  sudo bash ramban_deploy_s2t.sh" -ForegroundColor Cyan
}
