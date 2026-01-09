# Production Server Rules

## Golden Rule
**NEVER edit code files directly on the production server.**

## What This Means

### ❌ NEVER Do This on Production
- Edit `requirements.txt`
- Edit any `.py` files
- Edit templates
- Edit static files
- Manually install packages with `pip install`

### ✅ ALWAYS Do This Instead
1. Make changes in your local dev environment
2. Test locally
3. Commit to GitHub
4. Deploy via `git pull`

## Why This Matters

When you edit files on the server:
- Git sees them as "uncommitted changes"
- `git pull` refuses to overwrite them
- Deployment fails
- You waste time debugging

## Environment-Specific Config

If you need server-specific settings:

### Use `.env` (Already Gitignored)
```bash
# Edit this freely on server
nano /var/www/scan2talk/.env
```

### Use `requirements-prod.txt` (If Needed)
```bash
# In your repo, create:
requirements-prod.txt  # Production-only deps
requirements-dev.txt   # Dev-only deps
requirements.txt       # Common deps
```

## If Deployment Fails with "Local Changes"

### Quick Fix (Discard Server Changes)
```bash
cd /var/www/scan2talk
git reset --hard
git pull origin main
```

### If You Need to Save the Change
```bash
cd /var/www/scan2talk
git stash              # Save the change
git pull origin main   # Pull updates
git stash list         # See what was saved
# Later, if needed:
git stash apply        # Restore the change
```

## Lock Down Production (Recommended)

Make the server read-only for code:

```bash
# Set ownership to deployment user only
sudo chown -R www-data:www-data /var/www/scan2talk
sudo chmod -R 755 /var/www/scan2talk

# Only .env and media/logs should be writable
sudo chmod 644 /var/www/scan2talk/.env
sudo chmod -R 775 /var/www/scan2talk/media
sudo chmod -R 775 /var/www/scan2talk/logs
```

## Current Issue Resolution

Your deployment script (`ramban_deploy_s2t.sh`) is fine. The process is broken.

**Fix it now:**
```bash
ssh ramban@103.127.29.171
cd /var/www/scan2talk
git reset --hard
git pull origin main
```

Then never edit production files again.
