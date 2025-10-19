import psycopg2
import sys

# Database credentials from Lambda
DB_CONFIG = {
    'host': 'translatecloud-db-prod.cjpwzdyh1xn4.eu-west-1.rds.amazonaws.com',
    'database': 'translatecloud',
    'user': 'apiuser',
    'password': 'ApiUser2025Secure!',
    'port': 5432
}

try:
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check users table schema
    print("\n=== USERS TABLE SCHEMA ===")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """)

    columns = cursor.fetchall()
    print(f"{'Column':<30} {'Type':<20} {'Nullable':<10} {'Default':<20}")
    print("=" * 80)

    has_password_hash = False
    for col in columns:
        print(f"{col[0]:<30} {col[1]:<20} {col[2]:<10} {str(col[3] or ''):<20}")
        if col[0] == 'password_hash':
            has_password_hash = True

    print("\n=== MIGRATION STATUS ===")
    if has_password_hash:
        print("✅ password_hash column EXISTS")
    else:
        print("❌ password_hash column MISSING - Migration needed!")

    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\nTotal users in database: {user_count}")

    # Sample a user (if any)
    if user_count > 0:
        cursor.execute("SELECT id, email, password_hash IS NOT NULL as has_password, plan FROM users LIMIT 1")
        sample_user = cursor.fetchone()
        print(f"\nSample user:")
        print(f"  ID: {sample_user[0]}")
        print(f"  Email: {sample_user[1]}")
        print(f"  Has Password: {sample_user[2]}")
        print(f"  Plan: {sample_user[3]}")

    cursor.close()
    conn.close()
    print("\n✅ Database check complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
