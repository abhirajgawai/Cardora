"""
Fix cardora_user password using postgres superuser
"""
import sys
import os

# Fix encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

import psycopg

print("="*60)
print("Fixing cardora_user with postgres superuser")
print("="*60)

from urllib.parse import quote_plus

postgres_password = "Password890)"
# URL encode the password to handle special characters
postgres_password_encoded = quote_plus(postgres_password)

try:
    # Connect as postgres superuser
    print("\n[1/5] Connecting as postgres superuser...")
    print(f"      Using password: Password890) (encoded as: {postgres_password_encoded})")
    conn = psycopg.connect(
        f"postgresql://postgres:{postgres_password_encoded}@localhost:5432/postgres"
    )
    print("      [OK] Connected!")

    # Check if cardora_dev database exists
    print("\n[2/5] Checking if cardora_dev database exists...")
    cursor = conn.execute("SELECT 1 FROM pg_database WHERE datname = 'cardora_dev';")
    if cursor.fetchone():
        print("      [OK] Database 'cardora_dev' exists")
    else:
        print("      [ERROR] Database 'cardora_dev' does NOT exist!")
        print("      Creating database...")
        conn.execute("CREATE DATABASE cardora_dev;")
        conn.commit()
        print("      [OK] Database created!")

    # Check if cardora_user exists
    print("\n[3/5] Checking if cardora_user exists...")
    cursor = conn.execute("SELECT 1 FROM pg_user WHERE usename = 'cardora_user';")
    if cursor.fetchone():
        print("      [OK] User 'cardora_user' exists")
        print("      Resetting password...")
        conn.execute("ALTER USER cardora_user WITH PASSWORD 'cardora_secure_pass_2025';")
        conn.commit()
        print("      [OK] Password reset!")
    else:
        print("      [INFO] User does not exist, creating...")
        conn.execute("CREATE USER cardora_user WITH PASSWORD 'cardora_secure_pass_2025';")
        conn.commit()
        print("      [OK] User created!")

    # Grant privileges
    print("\n[4/5] Granting privileges to cardora_user...")
    conn.execute("GRANT ALL PRIVILEGES ON DATABASE cardora_dev TO cardora_user;")
    conn.commit()
    print("      [OK] Database privileges granted!")

    conn.close()

    # Now connect to cardora_dev to set schema privileges
    print("\n[5/5] Setting schema privileges...")
    conn2 = psycopg.connect(
        f"postgresql://postgres:{postgres_password_encoded}@localhost:5432/cardora_dev"
    )
    conn2.execute("GRANT ALL ON SCHEMA public TO cardora_user;")
    conn2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cardora_user;")
    conn2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cardora_user;")
    conn2.commit()
    conn2.close()
    print("      [OK] Schema privileges granted!")

    # Test connection as cardora_user
    print("\n" + "="*60)
    print("Testing connection as cardora_user...")
    print("="*60)

    conn3 = psycopg.connect(
        "postgresql://cardora_user:cardora_secure_pass_2025@localhost:5432/cardora_dev"
    )
    print("\n[SUCCESS] Connection works!")
    print(f"          User: {conn3.info.user}")
    print(f"          Database: {conn3.info.dbname}")
    print("\n" + "="*60)
    print("All fixed! Now run: python test_db_connection.py")
    print("="*60)
    conn3.close()

except psycopg.OperationalError as e:
    print(f"\n[ERROR] {e}")
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
