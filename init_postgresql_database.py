"""
PostgreSQL Database Initialization
Creates all tables in PostgreSQL database
"""

import psycopg2
from psycopg2 import sql
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLInitializer:
    """Initializes PostgreSQL database with all required tables"""
    
    def __init__(self, postgres_config: Dict[str, str]):
        self.postgres_config = postgres_config
        self.conn = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.postgres_config)
            self.conn.autocommit = False
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Closed PostgreSQL connection")
    
    def create_tables(self):
        """Create all required tables"""
        try:
            cursor = self.conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    hashed_password VARCHAR(255) NOT NULL,
                    risk_profile VARCHAR(50) DEFAULT 'moderate',
                    kyc_status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created users table")
            
            # Goals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    target_amount NUMERIC(15, 2) NOT NULL,
                    current_amount NUMERIC(15, 2) DEFAULT 0,
                    target_date DATE NOT NULL,
                    monthly_contribution NUMERIC(15, 2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created goals table")
            
            # Investments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    symbol VARCHAR(50) NOT NULL,
                    name VARCHAR(255),
                    type VARCHAR(50) NOT NULL,
                    quantity NUMERIC(15, 4) NOT NULL,
                    average_cost NUMERIC(15, 4) NOT NULL,
                    current_price NUMERIC(15, 4) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created investments table")
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    investment_id INTEGER REFERENCES investments(id) ON DELETE CASCADE,
                    type VARCHAR(50) NOT NULL,
                    quantity NUMERIC(15, 4) NOT NULL,
                    price NUMERIC(15, 4) NOT NULL,
                    amount NUMERIC(15, 2) NOT NULL,
                    fees NUMERIC(15, 2) DEFAULT 0,
                    date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created transactions table")
            
            # Market Prices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_prices (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(50) NOT NULL,
                    price NUMERIC(15, 4) NOT NULL,
                    change NUMERIC(15, 4) DEFAULT 0,
                    change_percent NUMERIC(10, 4) DEFAULT 0,
                    high NUMERIC(15, 4) DEFAULT 0,
                    low NUMERIC(15, 4) DEFAULT 0,
                    volume BIGINT DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created market_prices table")
            
            # Simulations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                    scenario_name VARCHAR(255) NOT NULL,
                    assumptions JSONB,
                    results JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created simulations table")
            
            # Portfolio Snapshots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    total_value NUMERIC(15, 2) NOT NULL,
                    cash_balance NUMERIC(15, 2) DEFAULT 0,
                    investments_value NUMERIC(15, 2) DEFAULT 0,
                    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    asset_allocation JSONB,
                    snapshot_data JSONB
                );
            """)
            logger.info("Created portfolio_snapshots table")
            
            # Performance Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    period VARCHAR(50) NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP NOT NULL,
                    total_return NUMERIC(10, 6) DEFAULT 0,
                    annualized_return NUMERIC(10, 6) DEFAULT 0,
                    volatility NUMERIC(10, 6) DEFAULT 0,
                    sharpe_ratio NUMERIC(10, 6) DEFAULT 0,
                    max_drawdown NUMERIC(10, 6) DEFAULT 0,
                    win_rate NUMERIC(10, 6) DEFAULT 0,
                    benchmark_return NUMERIC(10, 6) DEFAULT 0,
                    excess_return NUMERIC(10, 6) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created performance_metrics table")
            
            # User Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_alerts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    alert_type VARCHAR(50) NOT NULL,
                    symbol VARCHAR(50),
                    condition VARCHAR(50) NOT NULL,
                    threshold NUMERIC(15, 4) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_triggered BOOLEAN DEFAULT FALSE,
                    notification_method VARCHAR(50) DEFAULT 'email',
                    frequency VARCHAR(50) DEFAULT 'once',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP,
                    last_notified TIMESTAMP
                );
            """)
            logger.info("Created user_alerts table")
            
            # Recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    recommendation_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    reasoning TEXT,
                    suggested_allocation JSONB,
                    confidence_score NUMERIC(5, 4),
                    priority VARCHAR(50) DEFAULT 'medium',
                    status VARCHAR(50) DEFAULT 'pending',
                    implemented_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                );
            """)
            logger.info("Created recommendations table")
            
            # User Preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    dashboard_layout JSONB,
                    chart_preferences JSONB,
                    notification_settings JSONB,
                    theme VARCHAR(50) DEFAULT 'dark',
                    chart_colors JSONB,
                    risk_tolerance VARCHAR(50) DEFAULT 'moderate',
                    max_portfolio_volatility NUMERIC(10, 6) DEFAULT 0.15,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created user_preferences table")
            
            # Market Insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_insights (
                    id SERIAL PRIMARY KEY,
                    insight_type VARCHAR(50) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    symbols JSONB,
                    sentiment VARCHAR(50),
                    confidence NUMERIC(5, 4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created market_insights table")
            
            # Asset Allocation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_allocations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    target_allocation JSONB NOT NULL,
                    actual_allocation JSONB NOT NULL,
                    drift_threshold NUMERIC(10, 6) DEFAULT 0.05,
                    last_rebalanced TIMESTAMP,
                    next_rebalance_due TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("Created asset_allocations table")
            
            # Create indexes for better performance
            self.create_indexes(cursor)
            
            self.conn.commit()
            logger.info("All tables created successfully")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def create_indexes(self, cursor):
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_investments_user_id ON investments(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_investments_symbol ON investments(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_investment_id ON transactions(investment_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)",
            "CREATE INDEX IF NOT EXISTS idx_market_prices_symbol ON market_prices(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_market_prices_timestamp ON market_prices(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_simulations_user_id ON simulations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_simulations_goal_id ON simulations(goal_id)",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_id ON portfolio_snapshots(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_user_id ON performance_metrics(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON user_alerts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")
        
        logger.info("Indexes created successfully")
    
    def run_initialization(self):
        """Run the complete initialization process"""
        try:
            logger.info("Starting PostgreSQL database initialization...")
            
            # Connect to database
            self.connect()
            
            # Create all tables
            self.create_tables()
            
            logger.info("PostgreSQL database initialization completed successfully!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
        finally:
            self.close()


def main():
    """Main initialization function"""
    # PostgreSQL configuration
    postgres_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'wealth_management',
        'user': 'postgres',
        'password': 'your_password_here'
    }
    
    # Create initializer instance
    initializer = PostgreSQLInitializer(postgres_config)
    
    # Run initialization
    initializer.run_initialization()


if __name__ == "__main__":
    main()
