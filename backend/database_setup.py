import os
import sqlite3
from database import engine, Base

def create_sqlite_database():
    """Create SQLite database and tables"""
    try:
        # Create SQLite database file
        conn = sqlite3.connect('wealth_management.db')
        conn.close()
        
        # Update database URL for SQLite
        os.environ['DATABASE_URL'] = 'sqlite:///./wealth_management.db'
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("SQLite database and tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_sqlite_database()
