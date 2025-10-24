"""
Simple connection test with different password formats
"""
import sys
import os

if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

import psycopg

passwords_to_try = [
    ("Raw password", "Password890)"),
    ("URL encoded", "Password890%29"),
    ("Double escaped", "Password890))"),
]

print("Testing different password formats for postgres user...\n")

for name, password in passwords_to_try:
    print(f"Trying: {name} -> {password}")
    try:
        conn = psycopg.connect(
            host="localhost",
            port=5432,
            dbname="cardora_dev",
            user="postgres",
            password=password
        )
        print(f"  [SUCCESS!] Connection works with: {name}")
        print(f"  Database: {conn.info.dbname}")
        conn.close()
        print(f"\n  The correct password format is: {password}")
        break
    except psycopg.OperationalError as e:
        print(f"  [FAILED] {str(e)[:80]}...\n")
else:
    print("\n[ERROR] None of the password formats worked!")
    print("Please double-check your postgres password in pgAdmin")
