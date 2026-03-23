from celery import current_app
from celery_config import celery_app, DEFAULT_SYMBOLS
from database import SessionLocal
from services.market_service import market_service
from models_pkg.market import MarketPrice
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def update_market_prices_daily(self):
    """
    Background task to update market prices daily
    """
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            logger.info("Starting daily market price update")
            
            # Fetch real-time prices for default symbols
            fetched_prices = market_service.fetch_real_time_prices(DEFAULT_SYMBOLS)
            
            if not fetched_prices:
                logger.warning("No prices fetched from market data API")
                return {"status": "failed", "message": "No prices fetched"}
            
            # Store prices in database
            stored_count = market_service.store_prices(db, fetched_prices)
            
            logger.info(f"Successfully updated {stored_count} market prices")
            
            return {
                "status": "success",
                "message": f"Updated {stored_count} prices",
                "prices_count": len(fetched_prices),
                "symbols_updated": list(fetched_prices.keys())
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in daily market price update: {e}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries * 60  # 2min, 4min, 8min
            raise self.retry(countdown=countdown)
        
        return {"status": "failed", "message": str(e)}

@celery_app.task(bind=True)
def update_specific_symbols(self, symbols: list):
    """
    Background task to update specific symbols
    """
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            logger.info(f"Updating prices for symbols: {symbols}")
            
            # Fetch real-time prices
            fetched_prices = market_service.fetch_real_time_prices(symbols)
            
            if not fetched_prices:
                logger.warning(f"No prices fetched for symbols: {symbols}")
                return {"status": "failed", "message": "No prices fetched"}
            
            # Store prices in database
            stored_count = market_service.store_prices(db, fetched_prices)
            
            logger.info(f"Successfully updated {stored_count} prices for specific symbols")
            
            return {
                "status": "success",
                "message": f"Updated {stored_count} prices",
                "symbols": symbols,
                "prices_count": len(fetched_prices)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error updating specific symbols: {e}")
        return {"status": "failed", "message": str(e)}

@celery_app.task
def cleanup_old_prices():
    """
    Background task to clean up old price data (keep only last 90 days)
    """
    try:
        from datetime import datetime, timedelta
        from models.market import MarketPrice
        
        # Create database session
        db = SessionLocal()
        
        try:
            logger.info("Starting cleanup of old price data")
            
            # Calculate cutoff date (90 days ago)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            # Delete old records
            old_records = db.query(MarketPrice).filter(
                MarketPrice.timestamp < cutoff_date
            )
            
            deleted_count = old_records.count()
            old_records.delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old price records")
            
            return {
                "status": "success",
                "message": f"Deleted {deleted_count} old records",
                "cutoff_date": cutoff_date.isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error cleaning up old prices: {e}")
        return {"status": "failed", "message": str(e)}

@celery_app.task
def test_market_connection():
    """
    Test task to verify market data connection
    """
    try:
        logger.info("Testing market data connection")
        
        # Test with a few popular symbols
        test_symbols = ["AAPL", "MSFT", "GOOGL"]
        fetched_prices = market_service.fetch_real_time_prices(test_symbols)
        
        if fetched_prices:
            logger.info(f"Market connection test successful. Fetched {len(fetched_prices)} prices")
            return {
                "status": "success",
                "message": "Market connection working",
                "test_symbols": test_symbols,
                "prices": fetched_prices
            }
        else:
            logger.error("Market connection test failed - no prices fetched")
            return {
                "status": "failed",
                "message": "No prices fetched during test"
            }
            
    except Exception as e:
        logger.error(f"Market connection test error: {e}")
        return {
            "status": "failed",
            "message": str(e)
        }
