from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from database import get_db
from services.market_service import market_service
from services.market_data_service import market_data_service
from models_pkg.market import MarketPrice
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: str

class PriceUpdateResponse(BaseModel):
    success: bool
    message: str
    updated_count: int
    prices: Dict[str, float]

@router.get("/prices", response_model=Dict[str, float])
async def get_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols (e.g., AAPL,TSLA,MSFT)"),
    db: Session = Depends(get_db)
):
    """
    Get latest market prices for specified symbols
    If no symbols provided, returns all available prices
    """
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        prices = market_service.get_latest_prices(db, symbol_list)
        
        if not prices:
            return {}
        
        return prices
        
    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market prices")

@router.post("/update", response_model=PriceUpdateResponse)
async def update_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols to update"),
    db: Session = Depends(get_db)
):
    """
    Fetch and store latest market prices
    If no symbols provided, fetches default popular symbols
    """
    try:
        # Default symbols if none provided
        default_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA", "BTC-USD", "ETH-USD"]
        
        symbol_list = default_symbols
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        # Fetch real-time prices
        fetched_prices = market_service.fetch_real_time_prices(symbol_list)
        
        if not fetched_prices:
            return PriceUpdateResponse(
                success=False,
                message="Failed to fetch any prices",
                updated_count=0,
                prices={}
            )
        
        # Store prices in database
        stored_count = market_service.store_prices(db, fetched_prices)
        
        return PriceUpdateResponse(
            success=True,
            message=f"Successfully updated {stored_count} prices",
            updated_count=stored_count,
            prices=fetched_prices
        )
        
    except Exception as e:
        logger.error(f"Error updating prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to update market prices")

@router.get("/history/{symbol}")
async def get_price_history(
    symbol: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history to fetch"),
    db: Session = Depends(get_db)
):
    """
    Get historical price data for a specific symbol
    """
    try:
        symbol = symbol.upper().strip()
        history = market_service.get_price_history(db, symbol, days)
        
        if not history:
            raise HTTPException(status_code=404, detail=f"No price history found for {symbol}")
        
        return {
            "symbol": symbol,
            "history": history,
            "days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price history")

@router.get("/symbols")
async def get_available_symbols(db: Session = Depends(get_db)):
    """
    Get list of all available symbols in the database
    """
    try:
        from models.market import MarketPrice
        
        symbols = db.query(MarketPrice.symbol).distinct().all()
        return {"symbols": [s[0] for s in symbols]}
        
    except Exception as e:
        logger.error(f"Error getting available symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch available symbols")

# Real-time Market Data Endpoints

@router.get("/realtime/price/{symbol}")
async def get_realtime_price(symbol: str):
    """
    Get real-time stock price from Yahoo Finance
    """
    try:
        symbol = symbol.upper().strip()
        data = market_data_service.get_stock_price(symbol)
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error getting realtime price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/historical/{symbol}")
async def get_realtime_historical(symbol: str, period: str = "1mo"):
    """
    Get historical price data from Yahoo Finance
    """
    try:
        symbol = symbol.upper().strip()
        data = market_data_service.get_historical_data(symbol, period)
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/multiple")
async def get_multiple_realtime_prices(symbols: str = Query(..., description="Comma-separated symbols")):
    """
    Get real-time prices for multiple stocks
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        data = market_data_service.get_multiple_stocks(symbol_list)
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error getting multiple realtime prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/indices")
async def get_market_indices():
    """
    Get major market indices (S&P 500, NASDAQ, DOW)
    """
    try:
        data = market_data_service.get_market_indices()
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/search")
async def search_stocks(query: str = Query(..., description="Search query")):
    """
    Search for stocks by name or symbol
    """
    try:
        data = market_data_service.search_stocks(query)
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime/news/{symbol}")
async def get_stock_news(symbol: str, count: int = 5):
    """
    Get recent news for a stock
    """
    try:
        symbol = symbol.upper().strip()
        data = market_data_service.get_stock_news(symbol, count)
        return {"success": True, "data": data}
        
    except Exception as e:
        logger.error(f"Error getting stock news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
