# Automated Deployment Guide

## Quick Deployment Script

The `ramban_deploy_s2t.sh` script automates the entire deployment process for Scan2Talk.

### What It Does

1. ✅ Backs up your database
2. ✅ Pulls latest code from GitHub
3. ✅ Installs/updates Python dependencies
4. ✅ Runs database migrations
5. ✅ Collects static files
6. ✅ Restarts Gunicorn service
7. ✅ Restarts Nginx service
8. ✅ Verifies services are running
9. ✅ Cleans up old backups (keeps last 10)

### Setup (One-Time)

On your server, make the script executable:

```bash
cd /var/www/scan2talk
chmod +x ramban_deploy_s2t.sh
```

### Usage

Whenever you push code changes to GitHub, deploy them to your server:

```bash
# SSH into your server
ssh root@68.183.91.15

# Run the deployment script
cd /var/www/scan2talk
sudo ./ramban_deploy_s2t.sh
```

That's it! The script will automatically:
- Pull your latest code
- Update dependencies
- Run migrations
- Restart services
- Verify everything is working

### Typical Workflow

1. **Make changes locally** (on your Windows machine)
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```
3. **Deploy to server:**
   ```bash
   ssh root@68.183.91.15
   cd /var/www/scan2talk
   sudo ./ramban_deploy_s2t.sh
   ```

### Backup Location

Database backups are stored in: `/var/www/scan2talk/backups/`

Format: `db_backup_YYYYMMDD_HHMMSS.sqlite3`

The script automatically keeps the last 10 backups and deletes older ones.

### Troubleshooting

If deployment fails:

1. **Check the error message** - the script will show exactly what failed
2. **View service logs:**
   ```bash
   sudo journalctl -u gunicorn -n 50
   sudo tail -f /var/log/nginx/error.log
   ```
3. **Manually restart services:**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

### Manual Deployment (if script fails)

If you need to deploy manually:

```bash
cd /var/www/scan2talk
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Advanced: Automatic Deployment with Git Hooks

For fully automated deployment (deploy on every push), you can set up GitHub Actions or a Git webhook. Contact your DevOps team or refer to GitHub Actions documentation.

---

**Created by:** Ramban (Kiro AI Assistant)  
**Last Updated:** January 6, 2026
