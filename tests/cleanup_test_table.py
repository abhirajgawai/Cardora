"""Quick cleanup of test table"""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS test_connection'))
    conn.commit()
    print('✓ Test table cleaned up successfully!')
