"""
Quick script to verify cardora_user exists in PostgreSQL
"""
import psycopg

# Try to connect as cardora_user
try:
    conn = psycopg.connect(
        "postgresql://cardora_user:cardora_secure_pass_2025@localhost:5432/cardora_dev"
    )
    print("✅ SUCCESS! Connection works with cardora_user")
    print(f"Connected to: {conn.info.dbname}")
    print(f"User: {conn.info.user}")
    conn.close()
except psycopg.OperationalError as e:
    print("❌ Connection failed!")
    print(f"Error: {e}")
    print("\nPossible causes:")
    print("1. Password mismatch - password in .env doesn't match PostgreSQL")
    print("2. User doesn't exist - check pgAdmin Login/Group Roles")
    print("3. User lacks privileges - re-run GRANT commands")
