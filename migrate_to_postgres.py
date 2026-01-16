#!/usr/bin/env python
"""
Script to migrate SQLite database to PostgreSQL
Usage: python migrate_to_postgres.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_platform.settings')
django.setup()

from django.core.management import call_command
from django.db import connections
from django.apps import apps

def migrate_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""
    
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Step 1: Dump data from SQLite
    print("\n[1/4] Dumping data from SQLite...")
    try:
        call_command('dumpdata', 
                    '--natural-foreign', 
                    '--natural-primary',
                    '--exclude=contenttypes',
                    '--exclude=auth.permission',
                    '--indent=2',
                    output='db_backup.json')
        print("✓ Data dumped to db_backup.json")
    except Exception as e:
        print(f"✗ Error dumping data: {e}")
        return False
    
    # Step 2: Instructions for PostgreSQL setup
    print("\n[2/4] PostgreSQL Setup Instructions:")
    print("-" * 60)
    print("Run these commands in PostgreSQL (psql):")
    print("")
    print("  CREATE DATABASE scan2talk_db;")
    print("  CREATE USER postgres WITH PASSWORD 'Punit@1465';")
    print("  ALTER ROLE postgres SET client_encoding TO 'utf8';")
    print("  ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';")
    print("  ALTER ROLE postgres SET timezone TO 'UTC';")
    print("  GRANT ALL PRIVILEGES ON DATABASE scan2talk_db TO postgres;")
    print("")
    print("Or run: psql -U postgres -c \"CREATE DATABASE scan2talk_db;\"")
    print("-" * 60)
    
    input("\nPress Enter after PostgreSQL database is created...")
    
    # Step 3: Update settings and run migrations
    print("\n[3/4] Running migrations on PostgreSQL...")
    print("Note: Update your settings.py to use PostgreSQL before continuing")
    input("Press Enter after updating settings.py to PostgreSQL...")
    
    try:
        call_command('migrate', '--run-syncdb')
        print("✓ Migrations completed")
    except Exception as e:
        print(f"✗ Error running migrations: {e}")
        return False
    
    # Step 4: Load data into PostgreSQL
    print("\n[4/4] Loading data into PostgreSQL...")
    try:
        call_command('loaddata', 'db_backup.json')
        print("✓ Data loaded successfully")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        print("\nTip: If you see IntegrityError, you may need to:")
        print("  1. Drop and recreate the PostgreSQL database")
        print("  2. Run migrations again")
        print("  3. Try loading data again")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Migration completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Test your application")
    print("  2. Backup db_backup.json file")
    print("  3. Remove db.sqlite3 if everything works")
    
    return True

if __name__ == '__main__':
    success = migrate_to_postgres()
    sys.exit(0 if success else 1)
