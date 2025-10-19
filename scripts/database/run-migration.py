#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration Script
Runs add-password-auth.sql migration on RDS PostgreSQL database
"""

import psycopg2
from psycopg2 import sql
import json
import sys
import os
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Database credentials (from AWS Secrets Manager)
DB_CONFIG = {
    "host": "translatecloud-db-prod.c3asoiwiy0l1.eu-west-1.rds.amazonaws.com",
    "port": 5432,
    "database": "postgres",
    "user": "translatecloud_api",
    "password": "ApiUser2025Secure!"
}

def run_migration():
    """Run the database migration"""

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

    # Connect to database
    print(f"\n[*] Connecting to database...")
    print(f"    Host: {DB_CONFIG['host']}")
    print(f"    Database: {DB_CONFIG['database']}")
    print(f"    User: {DB_CONFIG['user']}")

    try:
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
        for col_name in new_columns:
            if col_name in existing_columns:
                print(f"  [OK] {col_name} - exists")
            else:
                print(f"  [MISSING] {col_name}")

        # Close connection
        cursor.close()
        conn.close()

        print("\n[OK] Migration verification complete!")
        print("\n[SUCCESS] Database is ready for password authentication!")

    except psycopg2.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TranslateCloud - Database Migration")
    print("Add Password Authentication Columns")
    print("=" * 60 + "\n")

    run_migration()
