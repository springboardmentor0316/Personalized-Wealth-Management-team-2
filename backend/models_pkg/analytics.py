from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class PortfolioSnapshot(Base):
    """Historical portfolio snapshots for performance tracking"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, default=0.0)
    investments_value = Column(Float, default=0.0)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    asset_allocation = Column(JSON)  # {sector: percentage, ...}
    snapshot_data = Column(JSON)  # Additional snapshot data
    
    # Relationships
    user = relationship("User")

class PerformanceMetrics(Base):
    """Calculated performance metrics for portfolios"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    period = Column(String(50))  # daily, weekly, monthly, yearly
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Performance metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    beta = Column(Float)
    alpha = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    
    # Benchmark comparison
    benchmark_return = Column(Float)
    excess_return = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class UserAlert(Base):
    """User-configured alerts for prices and portfolio changes"""
    __tablename__ = "user_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    alert_type = Column(String(50))  # price, portfolio, goal, news
    symbol = Column(String(20))  # Stock symbol for price alerts
    condition = Column(String(20))  # above, below, change_percent
    threshold_value = Column(Float)
    current_value = Column(Float)
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    notification_method = Column(String(20))  # email, push, sms
    frequency = Column(String(20))  # once, daily, weekly
    
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    last_notified = Column(DateTime)
    
    # Relationships
    user = relationship("User")

class Recommendation(Base):
    """AI-generated investment recommendations"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    recommendation_type = Column(String(50))  # portfolio, rebalancing, tax, risk
    title = Column(String(200))
    description = Column(Text)
    reasoning = Column(Text)
    
    # Recommendation data
    suggested_symbols = Column(JSON)  # [{symbol: "AAPL", action: "buy", weight: 0.1}, ...]
    expected_return = Column(Float)
    risk_level = Column(String(20))  # low, medium, high
    confidence_score = Column(Float)  # 0-1
    
    # Status
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    implemented_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")

class UserPreferences(Base):
    """User preferences for dashboard and notifications"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Dashboard preferences
    dashboard_layout = Column(JSON)  # Widget positions and sizes
    default_timeframe = Column(String(20), default="1M")
    preferred_charts = Column(JSON)  # Chart types and settings
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    price_alerts = Column(Boolean, default=True)
    portfolio_alerts = Column(Boolean, default=True)
    recommendation_alerts = Column(Boolean, default=True)
    
    # Theme preferences
    theme = Column(String(20), default="dark")
    chart_colors = Column(JSON)
    
    # Risk preferences
    risk_tolerance = Column(String(20), default="moderate")
    max_portfolio_volatility = Column(Float, default=0.15)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class MarketInsight(Base):
    """Market insights and analysis for recommendations"""
    __tablename__ = "market_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String(50))  # trend, sentiment, news, technical
    title = Column(String(200))
    content = Column(Text)
    symbols = Column(JSON)  # Related symbols
    sectors = Column(JSON)  # Related sectors
    
    # Analysis data
    sentiment_score = Column(Float)  # -1 to 1
    trend_direction = Column(String(20))  # bullish, bearish, neutral
    confidence = Column(Float)  # 0-1
    impact_level = Column(String(20))  # low, medium, high
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Metadata
    source = Column(String(100))  # Source of insight
    tags = Column(JSON)  # Searchable tags

class AssetAllocation(Base):
    """Target and current asset allocation for users"""
    __tablename__ = "asset_allocation"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Allocation targets
    stocks_percentage = Column(Float, default=0.6)
    bonds_percentage = Column(Float, default=0.3)
    real_estate_percentage = Column(Float, default=0.05)
    commodities_percentage = Column(Float, default=0.05)
    cash_percentage = Column(Float, default=0.0)
    
    # Current allocation (calculated)
    current_stocks = Column(Float, default=0.0)
    current_bonds = Column(Float, default=0.0)
    current_real_estate = Column(Float, default=0.0)
    current_commodities = Column(Float, default=0.0)
    current_cash = Column(Float, default=0.0)
    
    # Rebalancing
    rebalance_threshold = Column(Float, default=0.05)  # 5% deviation
    last_rebalanced = Column(DateTime)
    next_rebalance_due = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
