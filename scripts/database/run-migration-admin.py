#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script (Admin/Master User)
Runs add-password-auth.sql migration on RDS PostgreSQL database using master credentials
"""

import psycopg2
from psycopg2 import sql
import json
import sys
import os
import io
import getpass

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_migration():
    """Run the database migration with master user"""

    # Read the migration SQL file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, 'add-password-auth.sql')

    print(f"[*] Reading migration file: {sql_file}")

    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
    except FileNotFoundError:
        print(f"[ERROR] Migration file not found at {sql_file}")
        sys.exit(1)

    # Database configuration
    DB_CONFIG = {
        "host": "translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com",
        "port": 5432,
        "database": "postgres",
        "user": "postgres"
    }

    # Get password from user
    print(f"\n[*] Master user: {DB_CONFIG['user']}")
    print(f"[*] Database: {DB_CONFIG['database']}")
    print(f"[*] Host: {DB_CONFIG['host']}\n")

    # Master password from user's notes
    master_password = "TranslateCloud2025!"

    print(f"[*] Attempting connection with development master password...")

    # Connect to database
    try:
        DB_CONFIG['password'] = master_password
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()

        print("[OK] Connected successfully!\n")

        # Run migration
        print("[*] Running migration...")
        print("=" * 60)

        cursor.execute(migration_sql)

        # Commit transaction
        conn.commit()

        print("=" * 60)
        print("[OK] Migration completed successfully!\n")

        # Verify columns were added
        print("[*] Verifying new columns...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()

        print("\n[*] Current 'users' table schema:")
        print("-" * 60)
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            print(f"  {col[0]:<30} {col[1]:<20} {nullable}")
        print("-" * 60)

        # Check for new columns
        new_columns = [
            'password_hash',
            'words_used_this_month',
            'stripe_subscription_id',
            'subscription_tier',
            'stripe_customer_id',
            'subscription_status',
            'email_verified',
            'verification_token',
            'verification_token_expires',
            'last_login',
            'updated_at'
        ]

        existing_columns = [col[0] for col in columns]

        print("\n[*] Verification Results:")
        all_exist = True
        for col_name in new_columns:
            if col_name in existing_columns:
                print(f"  [OK] {col_name} - exists")
            else:
                print(f"  [MISSING] {col_name}")
                all_exist = False

        # Close connection
        cursor.close()
        conn.close()

        print("\n[OK] Migration verification complete!")

        if all_exist:
            print("\n[SUCCESS] Database is ready for password authentication!")
            return True
        else:
            print("\n[WARNING] Some columns are missing!")
            return False

    except psycopg2.OperationalError as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\n[INFO] The development master password didn't work.")
        print("[INFO] You need to run this migration manually using one of these methods:\n")
        print("METHOD 1: AWS RDS Query Editor")
        print("  1. Go to AWS Console -> RDS -> Query Editor")
        print("  2. Select database: translatecloud-db-prod")
        print("  3. Connect with master user (postgres)")
        print("  4. Paste the SQL from: scripts/database/add-password-auth.sql")
        print("  5. Click 'Run'\n")
        print("METHOD 2: pgAdmin or DBeaver")
        print("  1. Install pgAdmin or DBeaver")
        print("  2. Connect to: translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com")
        print("  3. Database: postgres, User: postgres, Port: 5432")
        print("  4. Run the SQL from: scripts/database/add-password-auth.sql\n")
        print("METHOD 3: Grant permissions to API user")
        print("  Run this SQL as master user:")
        print("  GRANT ALL PRIVILEGES ON TABLE users TO translatecloud_api;")
        print("  Then re-run: python scripts/database/run-migration.py\n")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TranslateCloud - Database Migration (Master User)")
    print("Add Password Authentication Columns")
    print("=" * 60 + "\n")

    run_migration()
