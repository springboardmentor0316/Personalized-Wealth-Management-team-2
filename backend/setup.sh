#!/bin/bash

echo "🚀 Setting up Wealth Management Backend - Milestone 3"
echo "=================================================="

# Check Python version
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python is not installed. Please install Python 3.8+"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check Redis
echo "🔍 Checking Redis connection..."
redis-cli ping > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Redis is not running. Please install and start Redis:"
    echo "   - Windows: Download Redis from https://redis.io/download"
    echo "   - macOS: brew install redis && brew start redis"
    echo "   - Linux: sudo apt-get install redis-server && sudo systemctl start redis"
    echo ""
    echo "   You can also run with Docker: docker run -d -p 6379:6379 redis:latest"
else
    echo "✅ Redis is running"
fi

# Create database tables
echo "🗄️  Creating database tables..."
python -c "from models import Base; from database import engine; Base.metadata.create_all(bind=engine)"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create database tables"
    exit 1
fi

echo "✅ Database tables created successfully"

# Test market data connection
echo "📈 Testing market data connection..."
python -c "from services.market_service import market_service; prices = market_service.fetch_real_time_prices(['AAPL']); print(f'✅ Market data test: {len(prices)} prices fetched')"

if [ $? -ne 0 ]; then
    echo "⚠️  Market data connection test failed (this might be due to network issues)"
else
    echo "✅ Market data connection working"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Make sure Redis is running"
echo "2. Start Celery worker: celery -A celery_config worker --loglevel=info"
echo "3. Start Celery beat: celery -A celery_config beat --loglevel=info"
echo "4. Start FastAPI server: python main.py"
echo ""
echo "🌐 API Documentation: http://localhost:8001/docs"
echo "📊 Market APIs: http://localhost:8001/market/prices"
echo "🧮 Simulation APIs: http://localhost:8001/simulate/"
echo "📋 Task Status: http://localhost:8001/tasks/status"
