import yfinance as yf
import sqlalchemy
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from models_pkg.market import MarketPrice
import logging

logger = logging.getLogger(__name__)

class MarketService:
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes cache
    
    def fetch_real_time_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch real-time prices for given symbols using yfinance
        """
        try:
            # Clean symbols and remove duplicates
            clean_symbols = list(set([s.upper().strip() for s in symbols if s]))
            
            if not clean_symbols:
                return {}
            
            # Fetch data using yfinance
            tickers = yf.Tickers(clean_symbols)
            prices = {}
            
            for symbol in clean_symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    # Get the most recent price
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        latest_price = hist['Close'].iloc[-1]
                        prices[symbol] = float(latest_price)
                    else:
                        logger.warning(f"No data found for symbol: {symbol}")
                        prices[symbol] = None
                except Exception as e:
                    logger.error(f"Error fetching price for {symbol}: {e}")
                    prices[symbol] = None
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching market prices: {e}")
            return {}
    
    def store_prices(self, db: Session, prices: Dict[str, float]) -> int:
        """
        Store fetched prices in database
        Returns number of prices stored successfully
        """
        stored_count = 0
        
        for symbol, price in prices.items():
            if price is not None:
                try:
                    market_price = MarketPrice(
                        symbol=symbol,
                        price=price,
                        timestamp=datetime.utcnow()
                    )
                    db.add(market_price)
                    stored_count += 1
                except Exception as e:
                    logger.error(f"Error storing price for {symbol}: {e}")
        
        try:
            db.commit()
            logger.info(f"Successfully stored {stored_count} market prices")
        except Exception as e:
            logger.error(f"Error committing prices to database: {e}")
            db.rollback()
            return 0
        
        return stored_count
    
    def get_latest_prices(self, db: Session, symbols: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Get latest prices from database
        """
        try:
            query = db.query(MarketPrice)
            
            if symbols:
                # Get latest price for each symbol
                clean_symbols = [s.upper().strip() for s in symbols if s]
                query = query.filter(MarketPrice.symbol.in_(clean_symbols))
            
            # Get the latest price for each symbol using subquery
            subquery = db.query(
                MarketPrice.symbol,
                MarketPrice.timestamp.label('max_timestamp')
            ).group_by(MarketPrice.symbol).subquery()
            
            latest_prices = db.query(MarketPrice).join(
                subquery,
                (MarketPrice.symbol == subquery.c.symbol) &
                (MarketPrice.timestamp == subquery.c.max_timestamp)
            ).all()
            
            return {price.symbol: price.price for price in latest_prices}
            
        except Exception as e:
            logger.error(f"Error getting latest prices: {e}")
            return {}
    
    def get_price_history(self, db: Session, symbol: str, days: int = 30) -> List[Dict]:
        """
        Get historical price data for a symbol
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            prices = db.query(MarketPrice).filter(
                MarketPrice.symbol == symbol.upper(),
                MarketPrice.timestamp >= start_date
            ).order_by(MarketPrice.timestamp.desc()).all()
            
            return [
                {
                    'price': price.price,
                    'timestamp': price.timestamp.isoformat()
                }
                for price in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return []

# Global instance
market_service = MarketService()
