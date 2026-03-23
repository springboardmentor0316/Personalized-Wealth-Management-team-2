# Milestone 3: Market Sync & Simulations

This milestone extends the existing Wealth Management application with real-time market data fetching, Celery background tasks, and investment simulation capabilities.

## 🚀 New Features

### 1. Market Data Module
- **Real-time price fetching** using Yahoo Finance (yfinance)
- **Automatic price updates** with Celery scheduled tasks
- **Historical price tracking** with database storage
- **Multiple asset support**: Stocks, ETFs, Crypto, Indices

### 2. Background Tasks with Celery
- **Daily price updates** at 11:30 PM UTC
- **Manual price updates** on-demand
- **Old data cleanup** (keeps 90 days)
- **Task monitoring** and status tracking

### 3. Investment Simulation Engine
- **Compound interest calculations**
- **SIP (Systematic Investment Plan) projections**
- **What-if scenario comparisons**
- **Goal-based projections**
- **Year-by-year breakdown**

## 📁 New File Structure

```
backend/
├── models/
│   └── market.py              # Market price data model
├── routes/
│   ├── market.py              # Market data API endpoints
│   └── simulation.py          # Simulation API endpoints
├── services/
│   ├── market_service.py      # Market data business logic
│   └── simulation_service.py  # Simulation calculations
├── tasks/
│   └── market_tasks.py        # Celery background tasks
├── celery_config.py           # Celery configuration
├── setup.bat                  # Windows setup script
├── setup.sh                   # Unix setup script
└── env.example               # Environment variables template
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Redis server
- Existing FastAPI backend

### Quick Setup (Windows)
```bash
# Run the setup script
setup.bat
```

### Quick Setup (Unix)
```bash
# Make setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (if not running)
redis-server

# Start Celery worker (Terminal 1)
celery -A celery_config worker --loglevel=info

# Start Celery beat (Terminal 2)
celery -A celery_config beat --loglevel=info

# Start FastAPI server (Terminal 3)
python main.py
```

## 📊 API Endpoints

### Market Data APIs

#### Get Latest Prices
```http
GET /market/prices?symbols=AAPL,TSLA,MSFT
```

#### Update Market Prices
```http
POST /market/update?symbols=AAPL,TSLA
```

#### Get Price History
```http
GET /market/history/AAPL?days=30
```

#### Get Available Symbols
```http
GET /market/symbols
```

### Simulation APIs

#### Basic Investment Simulation
```http
POST /simulate/
{
  "initial_amount": 100000,
  "monthly_investment": 5000,
  "annual_rate": 0.08,
  "years": 10
}
```

#### What-If Scenarios
```http
POST /simulate/what-if
{
  "initial_amount": 100000,
  "monthly_investment": 5000,
  "scenarios": [
    {"name": "Conservative", "annual_rate": 0.06, "years": 10},
    {"name": "Moderate", "annual_rate": 0.08, "years": 10},
    {"name": "Aggressive", "annual_rate": 0.12, "years": 10}
  ]
}
```

#### Goal Projection
```http
POST /simulate/goal-projection
{
  "target_amount": 1000000,
  "current_amount": 100000,
  "monthly_contribution": 10000,
  "annual_rate": 0.08
}
```

### Task Management APIs

#### Get Celery Status
```http
GET /tasks/status
```

#### Trigger Manual Market Update
```http
POST /tasks/market-update?symbols=AAPL,TSLA
```

#### Get Task Result
```http
GET /tasks/{task_id}
```

## 🔄 Background Tasks

### Scheduled Tasks
- **Daily Market Update**: Runs at 11:30 PM UTC
- **Weekly Cleanup**: Removes data older than 90 days

### Manual Tasks
- Trigger market updates for specific symbols
- Monitor task status and results

## 📈 Market Data Sources

### Supported Symbols
- **US Stocks**: AAPL, MSFT, GOOGL, TSLA, etc.
- **Indices**: SPY, QQQ, VTI, VOO
- **Crypto**: BTC-USD, ETH-USD
- **ETFs**: VTI, VOO, QQQ, SPY

### Data Refresh
- **Real-time fetching** using Yahoo Finance API
- **5-minute cache** for performance
- **Automatic daily updates** via Celery

## 🧮 Simulation Features

### Calculation Methods
- **Compound Interest**: A = P(1 + r/n)^(nt)
- **SIP Formula**: FV = P × [(1 + r)^n - 1] / r × (1 + r)
- **Goal Projection**: Iterative time calculation

### Output Features
- **Year-by-year breakdown**
- **Total returns and percentages**
- **Scenario comparisons**
- **Achievability analysis**

## 🔧 Configuration

### Environment Variables
```env
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Market Data
MARKET_UPDATE_ENABLED=true
ALPHA_VANTAGE_API_KEY=your-api-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Celery Configuration
- **Broker**: Redis
- **Result Backend**: Redis
- **Task Timeout**: 5 minutes
- **Result Expiry**: 1 hour

## 📱 Usage Examples

### Example 1: Fetch Market Prices
```python
import requests

# Get latest prices
response = requests.get("http://localhost:8001/market/prices?symbols=AAPL,TSLA")
prices = response.json()

# Update prices
response = requests.post("http://localhost:8001/market/update?symbols=AAPL,TSLA")
result = response.json()
```

### Example 2: Run Investment Simulation
```python
import requests

simulation_data = {
    "initial_amount": 100000,
    "monthly_investment": 5000,
    "annual_rate": 0.08,
    "years": 10
}

response = requests.post("http://localhost:8001/simulate/", json=simulation_data)
result = response.json()
```

### Example 3: Compare Scenarios
```python
import requests

scenarios = {
    "initial_amount": 100000,
    "monthly_investment": 5000,
    "scenarios": [
        {"name": "Safe", "annual_rate": 0.06, "years": 10},
        {"name": "Balanced", "annual_rate": 0.08, "years": 10},
        {"name": "Aggressive", "annual_rate": 0.12, "years": 10}
    ]
}

response = requests.post("http://localhost:8001/simulate/what-if", json=scenarios)
result = response.json()
```

## 🗄️ Database Schema

### Market Prices Table
```sql
CREATE TABLE market_prices (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    timestamp DATETIME NOT NULL,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);
```

## 🚨 Error Handling

### Market Data Errors
- **Network Issues**: Automatic retry with exponential backoff
- **Invalid Symbols**: Graceful handling with error logging
- **API Limits**: Rate limiting and caching

### Simulation Errors
- **Invalid Input**: Comprehensive validation with error messages
- **Calculation Errors**: Safe fallback with meaningful errors
- **Edge Cases**: Handling zero values and negative inputs

## 📊 Monitoring

### Celery Monitoring
- **Task Status**: `/tasks/status`
- **Individual Tasks**: `/tasks/{task_id}`
- **Worker Stats**: Available via Celery inspect

### Performance Metrics
- **API Response Times**: Built into FastAPI
- **Database Query Performance**: SQLAlchemy logging
- **Task Execution Time**: Celery monitoring

## 🔄 Integration with Existing Features

### Goals Module
- Link simulations to financial goals
- Show projected goal achievement
- Compare different investment strategies

### Portfolio Module
- Real-time portfolio valuation
- Performance tracking with market data
- Risk analysis with historical data

### User Module
- Personalized investment recommendations
- Risk-based scenario suggestions
- Goal tracking with projections

## 🎯 Next Steps

### Potential Enhancements
- **Alpha Vantage Integration**: For premium market data
- **Technical Indicators**: RSI, MACD, Moving Averages
- **Portfolio Optimization**: Modern Portfolio Theory
- **Risk Assessment**: Monte Carlo simulations
- **Tax Optimization**: Post-tax return calculations

### Performance Improvements
- **Database Indexing**: Optimize for time-series queries
- **Caching**: Redis for frequently accessed data
- **Async Processing**: Background market data updates
- **API Rate Limiting**: Prevent abuse

## 📞 Support

For issues and questions:
1. Check the logs: `celery -A celery_config worker --loglevel=info`
2. Verify Redis connection: `redis-cli ping`
3. Test market data: `GET /market/prices?symbols=AAPL`
4. Check API docs: `http://localhost:8001/docs`

---

**Milestone 3 Complete**: Market Sync & Simulations successfully integrated! 🎉
