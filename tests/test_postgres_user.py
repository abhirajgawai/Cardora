"""
Test connection with postgres superuser to verify PostgreSQL is working
"""
import sys
import os

# Fix encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

import psycopg

print("="*60)
print("Testing PostgreSQL Connection with postgres superuser")
print("="*60)

# Ask user for postgres password
postgres_password = input("\nEnter your 'postgres' superuser password: ")

try:
    # Test connection as postgres
    conn = psycopg.connect(
        f"postgresql://postgres:{postgres_password}@localhost:5432/cardora_dev"
    )
    print("\n[OK] Connected successfully as 'postgres' user!")
    print(f"    Database: {conn.info.dbname}")

    # Now check if cardora_user exists
    cursor = conn.execute("SELECT usename FROM pg_user WHERE usename = 'cardora_user';")
    result = cursor.fetchone()

    if result:
        print(f"\n[OK] User 'cardora_user' exists in PostgreSQL")

        # Try to see if we can reset the password
        print("\n[INFO] Attempting to reset cardora_user password...")
        conn.execute("ALTER USER cardora_user WITH PASSWORD 'cardora_secure_pass_2025';")
        conn.commit()
        print("[OK] Password reset successfully!")

    else:
        print("\n[ERROR] User 'cardora_user' does NOT exist!")
        print("       Would you like me to create it? (Run the CREATE USER command)")

    conn.close()

    # Now test connection as cardora_user
    print("\n" + "="*60)
    print("Testing connection as 'cardora_user'...")
    print("="*60)

    try:
        conn2 = psycopg.connect(
            "postgresql://cardora_user:cardora_secure_pass_2025@localhost:5432/cardora_dev"
        )
        print("\n[SUCCESS] Connection works with cardora_user!")
        print(f"           User: {conn2.info.user}")
        print(f"           Database: {conn2.info.dbname}")
        print("\n[OK] Ready to run: python test_db_connection.py")
        conn2.close()
    except psycopg.OperationalError as e:
        print("\n[ERROR] Still cannot connect as cardora_user")
        print(f"        Error: {e}")

except psycopg.OperationalError as e:
    print(f"\n[ERROR] Cannot connect as 'postgres' user!")
    print(f"        Error: {e}")
    print("\n[HELP] Check:")
    print("       1. Is PostgreSQL running?")
    print("       2. Is your postgres password correct?")
    print("       3. Does database 'cardora_dev' exist?")
