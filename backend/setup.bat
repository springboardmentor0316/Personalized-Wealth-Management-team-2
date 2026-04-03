@echo off
echo 🚀 Setting up Wealth Management Backend - Milestone 3
echo ==================================================

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install Python dependencies
    exit /b 1
)

REM Check Redis
echo 🔍 Checking Redis connection...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Redis is not running. Please install and start Redis:
    echo    - Windows: Download Redis from https://redis.io/download
    echo    - Docker: docker run -d -p 6379:6379 redis:latest
) else (
    echo ✅ Redis is running
)

REM Create database tables
echo 🗄️  Creating database tables...
python -c "from models import Base; from database import engine; Base.metadata.create_all(bind=engine)"

if %errorlevel% neq 0 (
    echo ❌ Failed to create database tables
    exit /b 1
)

echo ✅ Database tables created successfully

REM Test market data connection
echo 📈 Testing market data connection...
python -c "from services.market_service import market_service; prices = market_service.fetch_real_time_prices(['AAPL']); print(f'✅ Market data test: {len(prices)} prices fetched')"

if %errorlevel% neq 0 (
    echo ⚠️  Market data connection test failed (this might be due to network issues)
) else (
    echo ✅ Market data connection working
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next Steps:
echo 1. Make sure Redis is running
echo 2. Start Celery worker: celery -A celery_config worker --loglevel=info
echo 3. Start Celery beat: celery -A celery_config beat --loglevel=info
echo 4. Start FastAPI server: python main.py
echo.
echo 🌐 API Documentation: http://localhost:8001/docs
echo 📊 Market APIs: http://localhost:8001/market/prices
echo 🧮 Simulation APIs: http://localhost:8001/simulate/
echo 📋 Task Status: http://localhost:8001/tasks/status
pause
