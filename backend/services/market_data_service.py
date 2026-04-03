"""
Real-time Market Data Service
Integrates with Yahoo Finance API for live market data
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import time


class MarketDataService:
    """Service for fetching real-time market data from Yahoo Finance"""
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if available and not expired"""
        if key in self.cache:
            cached_time, data = self.cache[key]
            if time.time() - cached_time < self.cache_duration:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[key] = (time.time(), data)
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price and basic information
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "GOOGL", "TSLA")
            
        Returns:
            Dictionary with stock price data
        """
        try:
            cache_key = f"price_{symbol}"
            cached = self._get_cached_data(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/{symbol}"
            params = {
                "interval": "1d",
                "range": "1d",
                "includePrePost": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = self._parse_stock_data(symbol, data)
            self._set_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to fetch stock price for {symbol}: {str(e)}")
    
    def _parse_stock_data(self, symbol: str, data: Dict) -> Dict[str, Any]:
        """Parse Yahoo Finance response data"""
        try:
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            indicators = result.get("indicators", {})
            quote = indicators.get("quote", [{}])[0]
            
            current_price = None
            if quote and "close" in quote and quote["close"]:
                current_price = quote["close"][-1] if quote["close"][-1] else quote["open"][-1]
            
            previous_close = meta.get("previousClose", current_price)
            change = current_price - previous_close if current_price and previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close and previous_close > 0 else 0
            
            return {
                "symbol": symbol,
                "name": meta.get("longName", symbol),
                "current_price": round(current_price, 2) if current_price else 0,
                "previous_close": round(previous_close, 2) if previous_close else 0,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "high": round(meta.get("regularMarketDayHigh", 0), 2),
                "low": round(meta.get("regularMarketDayLow", 0), 2),
                "volume": meta.get("regularMarketVolume", 0),
                "market_cap": meta.get("marketCap", 0),
                "currency": meta.get("currency", "USD"),
                "exchange": meta.get("exchangeName", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse stock data: {str(e)}")
    
    def get_historical_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        Get historical price data
        
        Args:
            symbol: Stock symbol
            period: Time period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max")
            
        Returns:
            Dictionary with historical price data
        """
        try:
            cache_key = f"historical_{symbol}_{period}"
            cached = self._get_cached_data(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/{symbol}"
            params = {
                "interval": "1d",
                "range": period
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = self._parse_historical_data(symbol, data)
            self._set_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to fetch historical data for {symbol}: {str(e)}")
    
    def _parse_historical_data(self, symbol: str, data: Dict) -> Dict[str, Any]:
        """Parse historical data response"""
        try:
            result = data.get("chart", {}).get("result", [{}])[0]
            indicators = result.get("indicators", {})
            quote = indicators.get("quote", [{}])[0]
            
            timestamps = result.get("timestamp", [])
            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])
            volumes = quote.get("volume", [])
            
            historical_data = []
            for i in range(len(timestamps)):
                if i < len(closes) and closes[i] is not None:
                    historical_data.append({
                        "date": datetime.fromtimestamp(timestamps[i]).isoformat(),
                        "open": round(opens[i], 2) if opens[i] else None,
                        "high": round(highs[i], 2) if highs[i] else None,
                        "low": round(lows[i], 2) if lows[i] else None,
                        "close": round(closes[i], 2) if closes[i] else None,
                        "volume": volumes[i] if i < len(volumes) else None
                    })
            
            return {
                "symbol": symbol,
                "period": period,
                "data": historical_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse historical data: {str(e)}")
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get current prices for multiple stocks
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary with stock data for all symbols
        """
        try:
            results = {}
            for symbol in symbols:
                try:
                    results[symbol] = self.get_stock_price(symbol)
                except Exception as e:
                    results[symbol] = {
                        "symbol": symbol,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            return {
                "stocks": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch multiple stocks: {str(e)}")
    
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol
        
        Args:
            query: Search query
            
        Returns:
            List of matching stocks
        """
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                "q": query,
                "quotesCount": 10,
                "newsCount": 0
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            quotes = data.get("quotes", [])
            results = []
            
            for quote in quotes:
                results.append({
                    "symbol": quote.get("symbol", ""),
                    "name": quote.get("longname", quote.get("shortname", "")),
                    "type": quote.get("quoteType", ""),
                    "exchange": quote.get("exchange", ""),
                    "currency": quote.get("currency", "USD")
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to search stocks: {str(e)}")
    
    def get_market_indices(self) -> Dict[str, Any]:
        """
        Get major market indices (S&P 500, NASDAQ, DOW)
        
        Returns:
            Dictionary with market indices data
        """
        try:
            indices = {
                "S&P 500": "^GSPC",
                "NASDAQ": "^IXIC",
                "DOW JONES": "^DJI"
            }
            
            results = {}
            for name, symbol in indices.items():
                try:
                    data = self.get_stock_price(symbol)
                    results[name] = data
                except Exception as e:
                    results[name] = {
                        "symbol": symbol,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            return {
                "indices": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch market indices: {str(e)}")
    
    def get_stock_news(self, symbol: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent news for a stock
        
        Args:
            symbol: Stock symbol
            count: Number of news items
            
        Returns:
            List of news items
        """
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                "q": symbol,
                "quotesCount": 0,
                "newsCount": count
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            news_items = data.get("news", [])
            results = []
            
            for item in news_items[:count]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "published_at": item.get("providerPublishTime", ""),
                    "source": item.get("publisher", ""),
                    "summary": item.get("summary", "")
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to fetch stock news: {str(e)}")


# Global instance
market_data_service = MarketDataService()
