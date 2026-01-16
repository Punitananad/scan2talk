# SQLite to PostgreSQL Migration Guide

## Prerequisites

1. Install PostgreSQL on your system
2. Backup your current SQLite database

## Step-by-Step Migration

### Step 1: Install PostgreSQL (if not already installed)

**Windows:**
```bash
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Step 2: Create PostgreSQL Database

```bash
# Access PostgreSQL
psql -U postgres

# In PostgreSQL shell, run:
CREATE DATABASE scan2talk_db;
CREATE USER postgres WITH PASSWORD 'Punit@1465';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE scan2talk_db TO postgres;
\q
```

Or in one command:
```bash
psql -U postgres -c "CREATE DATABASE scan2talk_db;"
```

### Step 3: Backup Current SQLite Data

```bash
# Dump current data
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission --indent=2 > db_backup.json
```

### Step 4: Update Environment Configuration

Your `.env` file has been updated to:
```
DATABASE_URL=postgresql://postgres:Punit@1465@localhost:5432/scan2talk_db
```

### Step 5: Run Migrations on PostgreSQL

```bash
# Run migrations
python manage.py migrate --run-syncdb
```

### Step 6: Load Data into PostgreSQL

```bash
# Load the backed up data
python manage.py loaddata db_backup.json
```

### Step 7: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### Step 8: Test the Application

```bash
python manage.py runserver
```

Visit http://localhost:8000 and verify everything works.

## Automated Migration Script

Alternatively, use the provided script:

```bash
python migrate_to_postgres.py
```

## Troubleshooting

### Issue: IntegrityError during loaddata

**Solution:**
```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE scan2talk_db;"
psql -U postgres -c "CREATE DATABASE scan2talk_db;"

# Run migrations again
python manage.py migrate --run-syncdb

# Load data again
python manage.py loaddata db_backup.json
```

### Issue: Password authentication failed

**Solution:**
Check your PostgreSQL `pg_hba.conf` file and ensure it allows password authentication:
```
# Find pg_hba.conf location
psql -U postgres -c "SHOW hba_file;"

# Edit the file and change 'peer' to 'md5' for local connections
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
```

Then restart PostgreSQL:
```bash
# Linux
sudo systemctl restart postgresql

# Windows
net stop postgresql-x64-14
net start postgresql-x64-14
```

### Issue: Database doesn't exist

**Solution:**
```bash
# Create database manually
psql -U postgres -c "CREATE DATABASE scan2talk_db;"
```

## Production Deployment

For production server, update the `.env` on the server:

```bash
# On production server
cd /var/www/scan2talk
nano .env

# Update DATABASE_URL to:
DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD@localhost:5432/scan2talk_db
```

Then run migrations:
```bash
source venv/bin/activate
python manage.py migrate
```

## Rollback to SQLite (if needed)

If you need to rollback:

1. Update `.env`:
   ```
   DATABASE_URL=sqlite:///db.sqlite3
   ```

2. Your SQLite database (`db.sqlite3`) should still be intact

## Benefits of PostgreSQL

- ✅ Better performance for production
- ✅ Advanced features (JSON fields, full-text search)
- ✅ Better concurrency handling
- ✅ Industry standard for Django production
- ✅ Better data integrity
- ✅ Supports larger datasets

## Next Steps

1. ✅ Test all functionality
2. ✅ Backup `db_backup.json` file
3. ✅ Update production server
4. ✅ Monitor performance
5. ✅ Remove `db.sqlite3` after confirming everything works
