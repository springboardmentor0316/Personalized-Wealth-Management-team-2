from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

# Create Celery instance
celery_app = Celery(
    "wealth_management",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["tasks.market_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_track_started=True,
    task_time_limit=300,  # 5 minutes timeout per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'update-market-prices-daily': {
        'task': 'tasks.market_tasks.update_market_prices_daily',
        'schedule': crontab(hour=23, minute=30),  # Run at 11:30 PM UTC daily
    },
    'cleanup-old-prices': {
        'task': 'tasks.market_tasks.cleanup_old_prices',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Run weekly on Sunday at midnight
    },
}

# Default symbols to update
DEFAULT_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA", 
    "JPM", "BAC", "WMT", "HD", "PG", "JNJ", "UNH", "MA", "V",
    "BTC-USD", "ETH-USD", "SPY", "QQQ", "VTI", "VOO"
]
