"""
Celery Tasks for Scheduled Price Updates
Provides background tasks for updating market prices and portfolio values
"""

from celery import Celery, schedules
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Investment, User
from models_pkg.market import MarketPrice
from services.market_data_service import market_data_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    'wealth_management',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@celery_app.task(bind=True, name='update_market_prices')
def update_market_prices_task(self):
    """
    Update market prices for all tracked symbols
    
    Runs every 5 minutes
    """
    try:
        logger.info("Starting market price update task")
        
        db = SessionLocal()
        try:
            # Get all unique symbols from investments
            investments = db.query(Investment.symbol).distinct().all()
            symbols = [inv[0] for inv in investments]
            
            if not symbols:
                logger.info("No symbols found to update")
                return {"status": "success", "updated": 0, "message": "No symbols found"}
            
            # Fetch current prices for all symbols
            price_data = market_data_service.get_multiple_stocks(symbols)
            
            updated_count = 0
            for symbol, data in price_data.get("stocks", {}).items():
                if "error" not in data:
                    # Update or create market price record
                    existing_price = db.query(MarketPrice).filter(
                        MarketPrice.symbol == symbol
                    ).first()
                    
                    if existing_price:
                        existing_price.price = data.get("current_price", 0)
                        existing_price.change = data.get("change", 0)
                        existing_price.change_percent = data.get("change_percent", 0)
                        existing_price.high = data.get("high", 0)
                        existing_price.low = data.get("low", 0)
                        existing_price.volume = data.get("volume", 0)
                        existing_price.timestamp = datetime.utcnow()
                    else:
                        new_price = MarketPrice(
                            symbol=symbol,
                            price=data.get("current_price", 0),
                            change=data.get("change", 0),
                            change_percent=data.get("change_percent", 0),
                            high=data.get("high", 0),
                            low=data.get("low", 0),
                            volume=data.get("volume", 0),
                            timestamp=datetime.utcnow()
                        )
                        db.add(new_price)
                    
                    updated_count += 1
            
            db.commit()
            logger.info(f"Updated {updated_count} market prices")
            
            return {
                "status": "success",
                "updated": updated_count,
                "total_symbols": len(symbols),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating market prices: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


@celery_app.task(bind=True, name='update_portfolio_values')
def update_portfolio_values_task(self):
    """
    Update portfolio values for all users based on current market prices
    
    Runs every 10 minutes
    """
    try:
        logger.info("Starting portfolio value update task")
        
        db = SessionLocal()
        try:
            # Get all users
            users = db.query(User).all()
            
            updated_portfolios = 0
            for user in users:
                # Get all investments for user
                investments = db.query(Investment).filter(
                    Investment.user_id == user.id
                ).all()
                
                for investment in investments:
                    # Get current market price
                    market_price = db.query(MarketPrice).filter(
                        MarketPrice.symbol == investment.symbol
                    ).first()
                    
                    if market_price:
                        investment.current_price = market_price.price
                        investment.updated_at = datetime.utcnow()
                
                updated_portfolios += 1
            
            db.commit()
            logger.info(f"Updated portfolio values for {updated_portfolios} users")
            
            return {
                "status": "success",
                "updated_portfolios": updated_portfolios,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating portfolio values: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


@celery_app.task(bind=True, name='update_specific_symbol')
def update_specific_symbol_task(self, symbol: str):
    """
    Update price for a specific symbol
    
    Can be triggered manually or on-demand
    """
    try:
        logger.info(f"Updating price for symbol: {symbol}")
        
        db = SessionLocal()
        try:
            # Fetch current price
            price_data = market_data_service.get_stock_price(symbol)
            
            # Update or create market price record
            existing_price = db.query(MarketPrice).filter(
                MarketPrice.symbol == symbol
            ).first()
            
            if existing_price:
                existing_price.price = price_data.get("current_price", 0)
                existing_price.change = price_data.get("change", 0)
                existing_price.change_percent = price_data.get("change_percent", 0)
                existing_price.high = price_data.get("high", 0)
                existing_price.low = price_data.get("low", 0)
                existing_price.volume = price_data.get("volume", 0)
                existing_price.timestamp = datetime.utcnow()
            else:
                new_price = MarketPrice(
                    symbol=symbol,
                    price=price_data.get("current_price", 0),
                    change=price_data.get("change", 0),
                    change_percent=price_data.get("change_percent", 0),
                    high=price_data.get("high", 0),
                    low=price_data.get("low", 0),
                    volume=price_data.get("volume", 0),
                    timestamp=datetime.utcnow()
                )
                db.add(new_price)
            
            db.commit()
            logger.info(f"Successfully updated price for {symbol}")
            
            return {
                "status": "success",
                "symbol": symbol,
                "price": price_data.get("current_price", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating symbol {symbol}: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


@celery_app.task(bind=True, name='cleanup_old_market_prices')
def cleanup_old_market_prices_task(self):
    """
    Clean up old market price records (older than 30 days)
    
    Runs daily at midnight
    """
    try:
        logger.info("Starting cleanup of old market prices")
        
        db = SessionLocal()
        try:
            # Delete market prices older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted_count = db.query(MarketPrice).filter(
                MarketPrice.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Deleted {deleted_count} old market price records")
            
            return {
                "status": "success",
                "deleted": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up old prices: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


@celery_app.task(bind=True, name='send_price_alerts')
def send_price_alerts_task(self):
    """
    Check and send price alerts for triggered conditions
    
    Runs every 5 minutes
    """
    try:
        logger.info("Checking price alerts")
        
        db = SessionLocal()
        try:
            # This would integrate with the alerts system
            # For now, it's a placeholder
            
            logger.info("Price alert check completed")
            
            return {
                "status": "success",
                "alerts_triggered": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error checking price alerts: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    'update-market-prices-every-5-minutes': {
        'task': 'update_market_prices',
        'schedule': schedules.crontab(minute='*/5'),  # Every 5 minutes
    },
    'update-portfolio-values-every-10-minutes': {
        'task': 'update_portfolio_values',
        'schedule': schedules.crontab(minute='*/10'),  # Every 10 minutes
    },
    'cleanup-old-prices-daily': {
        'task': 'cleanup_old_market_prices',
        'schedule': schedules.crontab(hour=0, minute=0),  # Daily at midnight
    },
    'check-price-alerts-every-5-minutes': {
        'task': 'send_price_alerts',
        'schedule': schedules.crontab(minute='*/5'),  # Every 5 minutes
    },
}


if __name__ == '__main__':
    celery_app.start()
