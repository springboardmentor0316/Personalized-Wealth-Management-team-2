from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from database import Base
from datetime import datetime

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Create composite index for symbol and timestamp queries
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )

    def __repr__(self):
        return f"<MarketPrice(symbol={self.symbol}, price={self.price}, timestamp={self.timestamp})>"
