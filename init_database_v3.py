#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import all models individually
from database import engine, Base
from models import User, Goal, Investment, Transaction
from models_pkg.market import MarketPrice
from models_pkg.analytics import PortfolioSnapshot, PerformanceMetrics, UserAlert, Recommendation, UserPreferences, MarketInsight, AssetAllocation

def init_database():
    print("🔧 Initializing database...")
    
    try:
        # Import all models to register them with SQLAlchemy
        print("📋 Registering models...")
        all_models = [
            User, Goal, Investment, Transaction,
            MarketPrice,
            PortfolioSnapshot, PerformanceMetrics, UserAlert, 
            Recommendation, UserPreferences, MarketInsight, AssetAllocation
        ]
        
        for model in all_models:
            print(f"   ✓ {model.__name__}")
        
        # Create all tables
        print("\n🏗️  Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List all tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Total tables: {len(tables)}")
        for table in sorted(tables):
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()
