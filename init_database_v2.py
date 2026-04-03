#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, Base
from models import User, Goal, Investment, Transaction
from models_pkg.market import MarketPrice
from models_pkg.analytics import PortfolioSnapshot, PerformanceMetrics, UserAlert, Recommendation, UserPreferences, MarketInsight, AssetAllocation

def init_database():
    print("🔧 Initializing database...")
    
    try:
        # Manually register all models with Base
        models_to_register = [
            User, Goal, Investment, Transaction,
            MarketPrice,
            PortfolioSnapshot, PerformanceMetrics, UserAlert, 
            Recommendation, UserPreferences, MarketInsight, AssetAllocation
        ]
        
        for model in models_to_register:
            Base.metadata.register_model(model.__name__, model)
            print(f"   ✓ Registered {model.__name__}")
        
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
