# Production Deployment Checklist

## 🚀 Quick Deployment Steps

### Step 1: Push Changes to Repository
```bash
# Windows PowerShell
.\deploy_error_pages.ps1

# OR Linux/Mac
bash deploy_error_pages.sh
```

### Step 2: Deploy to Production Server
```bash
# SSH into production
ssh root@68.183.91.15

# Navigate to project
cd /root/CPA

# Pull latest changes
git pull origin main

# Collect static files
python manage.py collectstatic --noinput

# Restart services
systemctl restart gunicorn
systemctl restart nginx

# Check status
systemctl status gunicorn
systemctl status nginx
```

### Step 3: Verify Deployment
1. Visit: https://scan2talk.in/test-404
2. Should see custom 404 page (not URL patterns)
3. Click "Go to Homepage" - should work
4. Click "Go Back" - should work

## ✅ Pre-Deployment Checklist

- [ ] All changes committed to git
- [ ] Error handler files created
- [ ] Error templates created
- [ ] URLs.py updated with handlers
- [ ] Gateway detail template created
- [ ] Local testing completed (if possible)

## ✅ Post-Deployment Checklist

- [ ] Production site accessible
- [ ] Custom 404 page shows (not URL patterns)
- [ ] Navigation buttons work
- [ ] Mobile responsive
- [ ] No errors in logs
- [ ] Gunicorn running
- [ ] Nginx running

## 🔍 Troubleshooting

### If 404 page still shows URL patterns:
```bash
# Check DEBUG setting
grep DEBUG /root/CPA/.env

# Should show: DEBUG=False

# Restart services
systemctl restart gunicorn
systemctl restart nginx
```

### If error pages not loading:
```bash
# Check templates exist
ls -la /root/CPA/templates/errors/

# Check error handlers file
ls -la /root/CPA/apps/core/error_handlers.py

# Check logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/error.log
```

### If static files not loading:
```bash
# Collect static files again
cd /root/CPA
python manage.py collectstatic --noinput

# Check nginx static file configuration
nginx -t
systemctl restart nginx
```

## 📝 Important Notes

1. **DEBUG Setting**: Must be `False` in production
2. **ALLOWED_HOSTS**: Must include your domain
3. **Static Files**: Must be collected after deployment
4. **Services**: Must restart gunicorn and nginx

## 🎯 Success Criteria

✅ Visit https://scan2talk.in/nonexistent-page
✅ See custom 404 page (not URL patterns)
✅ Page looks professional
✅ Navigation works
✅ Mobile responsive
✅ No errors in logs

## 📞 Emergency Rollback

If something goes wrong:
```bash
# On production server
cd /root/CPA
git log --oneline -5  # See recent commits
git revert HEAD  # Revert last commit
systemctl restart gunicorn
systemctl restart nginx
```

## 🎉 Deployment Complete!

Once all checks pass, your production site is secure and professional!
