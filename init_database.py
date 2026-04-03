#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import all models to ensure they're registered
from database import engine, Base
import models  # Import all models
import models_pkg.market  # Import market models
import models_pkg.analytics  # Import analytics models

def init_database():
    print("🔧 Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    init_database()
