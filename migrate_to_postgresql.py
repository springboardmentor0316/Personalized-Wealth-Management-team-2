"""
PostgreSQL Migration Script
Migrates data from SQLite to PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2 import sql
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLMigrator:
    """Migrates data from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_db_path: str, postgres_config: Dict[str, str]):
        self.sqlite_db_path = sqlite_db_path
        self.postgres_config = postgres_config
        self.sqlite_conn = None
        self.postgres_conn = None
        
    def connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.sqlite_db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    def connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            self.postgres_conn.autocommit = False
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def close_connections(self):
        """Close all database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("Closed SQLite connection")
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("Closed PostgreSQL connection")
    
    def migrate_table(self, table_name: str, column_mapping: Dict[str, str] = None):
        """
        Migrate data from SQLite table to PostgreSQL
        
        Args:
            table_name: Name of the table to migrate
            column_mapping: Optional mapping of SQLite columns to PostgreSQL columns
        """
        try:
            # Read data from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                logger.info(f"No data found in table: {table_name}")
                return
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            logger.info(f"Found {len(rows)} rows in {table_name}")
            
            # Apply column mapping if provided
            if column_mapping:
                postgres_columns = [column_mapping.get(col, col) for col in columns]
            else:
                postgres_columns = columns
            
            # Insert data into PostgreSQL
            postgres_cursor = self.postgres_conn.cursor()
            
            for row in rows:
                row_dict = dict(zip(columns, row))
                
                # Handle enum values and special types
                processed_values = []
                for col in columns:
                    value = row_dict[col]
                    if value is None:
                        processed_values.append(None)
                    elif isinstance(value, str):
                        processed_values.append(value)
                    elif isinstance(value, (int, float)):
                        processed_values.append(value)
                    else:
                        processed_values.append(str(value))
                
                # Build INSERT query
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, postgres_columns)),
                    sql.SQL(', ').join([sql.Placeholder()] * len(postgres_columns))
                )
                
                postgres_cursor.execute(insert_query, processed_values)
            
            self.postgres_conn.commit()
            logger.info(f"Successfully migrated {len(rows)} rows from {table_name}")
            
        except Exception as e:
            self.postgres_conn.rollback()
            logger.error(f"Failed to migrate table {table_name}: {e}")
            raise
    
    def migrate_all_tables(self):
        """Migrate all tables from SQLite to PostgreSQL"""
        try:
            # Get list of tables from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in sqlite_cursor.fetchall()]
            
            logger.info(f"Found {len(tables)} tables to migrate: {tables}")
            
            # Define table migration order (respecting foreign keys)
            migration_order = [
                'users',
                'goals',
                'investments',
                'transactions',
                'market_prices',
                'simulations',
                'portfolio_snapshots',
                'performance_metrics',
                'user_alerts',
                'recommendations',
                'user_preferences',
                'market_insights',
                'asset_allocations'
            ]
            
            # Migrate tables in order
            for table_name in migration_order:
                if table_name in tables:
                    self.migrate_table(table_name)
                else:
                    logger.warning(f"Table {table_name} not found in SQLite database")
            
            logger.info("Migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def run_migration(self):
        """Run the complete migration process"""
        try:
            logger.info("Starting migration from SQLite to PostgreSQL...")
            
            # Connect to databases
            self.connect_sqlite()
            self.connect_postgres()
            
            # Migrate all tables
            self.migrate_all_tables()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            self.close_connections()


def main():
    """Main migration function"""
    # SQLite database path
    sqlite_db_path = "d:/infosys/backend/wealth_management.db"
    
    # PostgreSQL configuration
    postgres_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'wealth_management',
        'user': 'postgres',
        'password': 'your_password_here'
    }
    
    # Create migrator instance
    migrator = PostgreSQLMigrator(sqlite_db_path, postgres_config)
    
    # Run migration
    migrator.run_migration()


if __name__ == "__main__":
    main()
