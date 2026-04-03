"""Check and fix database schema"""
import sys
sys.path.insert(0, 'd:/infosys/backend')
from sqlalchemy import text, inspect
from database import engine

# Check users table schema
inspector = inspect(engine)
columns = inspector.get_columns('users')
print("Users table columns:")
for col in columns:
    print(f"  {col['name']}: {col['type']}")

# Check current data
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, email, risk_profile, kyc_status FROM users"))
    print("\nCurrent user data:")
    for row in result:
        print(f"  ID {row.id}: {row.email}, Risk={row.risk_profile}, KYC={row.kyc_status}")
