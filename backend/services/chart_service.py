from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from models_pkg.analytics import PortfolioSnapshot, PerformanceMetrics
from models_pkg.market import MarketPrice
from models import Investment, Transaction
from database import SessionLocal

class ChartService:
    """Advanced chart data preparation service"""
    
    def __init__(self):
        self.timeframes = {
            "1D": 1, "1W": 7, "1M": 30, "3M": 90, 
            "6M": 180, "1Y": 365, "ALL": 3650
        }
    
    def get_portfolio_performance_chart_data(self, user_id: int, timeframe: str = "1M", db: Session = None) -> Dict[str, Any]:
        """Get portfolio performance data for charting"""
        if db is None:
            db = SessionLocal()
        
        try:
            days = self.timeframes.get(timeframe, 30)
            
            # Get user's investments
            investments = db.query(Investment).filter(
                Investment.user_id == user_id
            ).all()
            
            if not investments:
                return self._empty_chart_data("portfolio_performance")
            
            # Calculate current total value
            current_value = sum(inv.quantity * inv.current_price for inv in investments)
            cost_basis = sum(inv.quantity * inv.average_cost for inv in investments)
            
            # Generate historical data points
            end_date = datetime.utcnow()
            dates = []
            values = []
            
            # Create data points for the timeframe
            for i in range(min(days, 30), 0, -1):
                date_point = end_date - timedelta(days=i)
                dates.append(date_point.strftime("%Y-%m-%d"))
                
                # Simulate gradual growth from cost basis to current value
                progress = 1 - (i / days)
                simulated_value = cost_basis + (current_value - cost_basis) * progress
                # Add small random variation
                variation = simulated_value * np.random.uniform(-0.02, 0.02)
                values.append(round(simulated_value + variation, 2))
            
            # Add current value
            dates.append(end_date.strftime("%Y-%m-%d"))
            values.append(round(current_value, 2))
            
            # Calculate moving averages
            ma_7 = self._calculate_moving_average(values, 7)
            ma_30 = self._calculate_moving_average(values, 30) if len(values) >= 30 else None
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(values)):
                if values[i-1] > 0:
                    ret = ((values[i] - values[i-1]) / values[i-1]) * 100
                    daily_returns.append(ret)
            
            chart_data = {
                "type": "portfolio_performance",
                "timeframe": timeframe,
                "data": {
                    "dates": dates,
                    "values": values,
                    "moving_averages": {
                        "ma_7": ma_7,
                        "ma_30": ma_30
                    },
                    "daily_returns": daily_returns,
                    "metadata": {
                        "start_value": values[0] if values else 0,
                        "end_value": values[-1] if values else 0,
                        "total_return": ((values[-1] - values[0]) / values[0] * 100) if values and values[0] > 0 else 0,
                        "volatility": np.std(daily_returns) if daily_returns else 0,
                        "max_value": max(values) if values else 0,
                        "min_value": min(values) if values else 0
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            raise Exception(f"Failed to get portfolio performance chart data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_asset_allocation_chart_data(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Get asset allocation data for pie chart from investments"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get user's investments with current prices
            investments = db.query(Investment).filter(
                Investment.user_id == user_id
            ).all()
            
            if not investments:
                return self._empty_chart_data("asset_allocation")
            
            # Calculate allocation by type
            allocation = {}
            total_value = 0
            
            for inv in investments:
                inv_type = inv.type if isinstance(inv.type, str) else inv.type.value
                value = inv.quantity * inv.current_price
                total_value += value
                allocation[inv_type] = allocation.get(inv_type, 0) + value
            
            # Convert to percentages
            if total_value > 0:
                for key in allocation:
                    allocation[key] = (allocation[key] / total_value) * 100
            
            # Prepare data for pie chart
            labels = list(allocation.keys())
            values = list(allocation.values())
            colors = self._get_sector_colors(labels)
            
            chart_data = {
                "type": "asset_allocation",
                "data": {
                    "labels": labels,
                    "values": values,
                    "colors": colors,
                    "percentages": [round(v, 1) for v in values],
                    "metadata": {
                        "total_value": total_value,
                        "number_of_sectors": len(allocation),
                        "largest_sector": max(allocation, key=allocation.get) if allocation else None,
                        "concentration_ratio": max(allocation.values()) / 100 if allocation else 0
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            raise Exception(f"Failed to get asset allocation chart data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_stock_price_chart_data(self, symbol: str, timeframe: str = "1M", db: Session = None) -> Dict[str, Any]:
        """Get stock price data for candlestick chart"""
        if db is None:
            db = SessionLocal()
        
        try:
            days = self.timeframes.get(timeframe, 30)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get price history
            prices = db.query(MarketPrice).filter(
                and_(
                    MarketPrice.symbol == symbol,
                    MarketPrice.timestamp >= start_date
                )
            ).order_by(MarketPrice.timestamp).all()
            
            if not prices:
                return self._empty_chart_data("stock_price")
            
            # Prepare OHLC data (simplified - using current price as close, generating mock OHLC)
            ohlc_data = []
            for i, price in enumerate(prices):
                # Generate realistic OHLC from closing prices
                close_price = price.price
                volatility = close_price * 0.02  # 2% intraday volatility
                
                if i == 0:
                    open_price = close_price
                else:
                    open_price = prices[i-1].price
                
                high_price = max(open_price, close_price) + np.random.uniform(0, volatility)
                low_price = min(open_price, close_price) - np.random.uniform(0, volatility)
                volume = np.random.randint(1000000, 10000000)  # Mock volume
                
                ohlc_data.append({
                    "date": price.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume
                })
            
            # Calculate technical indicators
            closes = [item["close"] for item in ohlc_data]
            sma_20 = self._calculate_moving_average(closes, 20)
            sma_50 = self._calculate_moving_average(closes, 50) if len(closes) >= 50 else None
            
            chart_data = {
                "type": "stock_price",
                "symbol": symbol,
                "timeframe": timeframe,
                "data": {
                    "ohlc": ohlc_data,
                    "technical_indicators": {
                        "sma_20": sma_20,
                        "sma_50": sma_50,
                        "rsi": self._calculate_rsi(closes) if len(closes) >= 14 else None,
                        "bollinger_bands": self._calculate_bollinger_bands(closes) if len(closes) >= 20 else None
                    },
                    "metadata": {
                        "current_price": closes[-1] if closes else 0,
                        "price_change": ((closes[-1] - closes[0]) / closes[0] * 100) if closes and closes[0] > 0 else 0,
                        "high_52w": max(closes) if closes else 0,
                        "low_52w": min(closes) if closes else 0,
                        "average_volume": np.mean([item["volume"] for item in ohlc_data])
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            raise Exception(f"Failed to get stock price chart data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_performance_comparison_chart_data(self, user_id: int, benchmark_symbols: List[str] = None, timeframe: str = "1M", db: Session = None) -> Dict[str, Any]:
        """Get performance comparison data"""
        if db is None:
            db = SessionLocal()
        
        try:
            if benchmark_symbols is None:
                benchmark_symbols = ["SPY", "QQQ"]
            
            days = self.timeframes.get(timeframe, 30)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get portfolio data
            portfolio_snapshots = db.query(PortfolioSnapshot).filter(
                and_(
                    PortfolioSnapshot.user_id == user_id,
                    PortfolioSnapshot.snapshot_date >= start_date
                )
            ).order_by(PortfolioSnapshot.snapshot_date).all()
            
            # Get benchmark data
            benchmark_data = {}
            for symbol in benchmark_symbols:
                prices = db.query(MarketPrice).filter(
                    and_(
                        MarketPrice.symbol == symbol,
                        MarketPrice.timestamp >= start_date
                    )
                ).order_by(MarketPrice.timestamp).all()
                
                if prices:
                    benchmark_data[symbol] = {
                        "dates": [p.timestamp.strftime("%Y-%m-%d %H:%M:%S") for p in prices],
                        "values": [p.price for p in prices]
                    }
            
            # Normalize all data to percentage change from start
            comparison_data = {
                "type": "performance_comparison",
                "timeframe": timeframe,
                "data": {
                    "dates": [s.snapshot_date.strftime("%Y-%m-%d %H:%M:%S") for s in portfolio_snapshots],
                    "portfolio": self._normalize_to_percentage([s.total_value for s in portfolio_snapshots]),
                    "benchmarks": {}
                }
            }
            
            # Normalize benchmark data
            for symbol, data in benchmark_data.items():
                comparison_data["data"]["benchmarks"][symbol] = self._normalize_to_percentage(data["values"])
            
            return comparison_data
            
        except Exception as e:
            raise Exception(f"Failed to get performance comparison chart data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_risk_return_scatter_data(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Get risk-return scatter plot data"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get performance metrics for different periods
            metrics = db.query(PerformanceMetrics).filter(
                PerformanceMetrics.user_id == user_id
            ).order_by(PerformanceMetrics.start_date).all()
            
            if not metrics:
                return self._empty_chart_data("risk_return_scatter")
            
            # Prepare scatter plot data
            scatter_data = []
            for metric in metrics:
                scatter_data.append({
                    "period": metric.period,
                    "return": metric.annualized_return * 100,  # Convert to percentage
                    "risk": metric.volatility * 100,  # Convert to percentage
                    "sharpe_ratio": metric.sharpe_ratio,
                    "date": metric.end_date.strftime("%Y-%m-%d")
                })
            
            # Add benchmark data
            benchmark_data = [
                {"period": "S&P 500", "return": 8.0, "risk": 15.0, "sharpe_ratio": 0.53},
                {"period": "US Bonds", "return": 3.0, "risk": 5.0, "sharpe_ratio": 0.60},
                {"period": "Gold", "return": 5.0, "risk": 20.0, "sharpe_ratio": 0.25}
            ]
            
            chart_data = {
                "type": "risk_return_scatter",
                "data": {
                    "portfolio": scatter_data,
                    "benchmarks": benchmark_data,
                    "metadata": {
                        "best_period": max(scatter_data, key=lambda x: x["sharpe_ratio"]) if scatter_data else None,
                        "average_return": np.mean([s["return"] for s in scatter_data]) if scatter_data else 0,
                        "average_risk": np.mean([s["risk"] for s in scatter_data]) if scatter_data else 0
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            raise Exception(f"Failed to get risk-return scatter data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_correlation_heatmap_data(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Get correlation heatmap data for portfolio holdings"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get user's investments
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            if len(investments) < 2:
                return self._empty_chart_data("correlation_heatmap")
            
            # Get price history for each investment
            price_data = {}
            days = 90  # 3 months of data
            
            for investment in investments:
                start_date = datetime.utcnow() - timedelta(days=days)
                prices = db.query(MarketPrice).filter(
                    and_(
                        MarketPrice.symbol == investment.symbol,
                        MarketPrice.timestamp >= start_date
                    )
                ).order_by(MarketPrice.timestamp).all()
                
                if len(prices) >= 30:  # Need at least 30 data points
                    price_data[investment.symbol] = [p.price for p in prices]
            
            # Calculate correlation matrix
            symbols = list(price_data.keys())
            correlation_matrix = []
            
            for i, symbol1 in enumerate(symbols):
                correlation_row = []
                for j, symbol2 in enumerate(symbols):
                    if i == j:
                        correlation_row.append(1.0)
                    else:
                        correlation = self._calculate_correlation(
                            price_data[symbol1], 
                            price_data[symbol2]
                        )
                        correlation_row.append(correlation)
                correlation_matrix.append(correlation_row)
            
            chart_data = {
                "type": "correlation_heatmap",
                "data": {
                    "symbols": symbols,
                    "matrix": correlation_matrix,
                    "metadata": {
                        "most_correlated": self._find_most_correlated(symbols, correlation_matrix),
                        "least_correlated": self._find_least_correlated(symbols, correlation_matrix),
                        "average_correlation": self._calculate_average_correlation(correlation_matrix)
                    }
                }
            }
            
            return chart_data
            
        except Exception as e:
            raise Exception(f"Failed to get correlation heatmap data: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def _calculate_moving_average(self, values: List[float], period: int) -> List[float]:
        """Calculate moving average"""
        if len(values) < period:
            return [None] * len(values)
        
        ma = []
        for i in range(len(values)):
            if i < period - 1:
                ma.append(None)
            else:
                avg = np.mean(values[i - period + 1:i + 1])
                ma.append(round(avg, 2))
        
        return ma
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return [None] * len(prices)
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        rsi = [None] * period
        rsi.append(100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 50)
        
        for i in range(period + 1, len(prices)):
            gain = gains[i - 1]
            loss = losses[i - 1]
            
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            
            rsi_value = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 50
            rsi.append(rsi_value)
        
        return rsi
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {"upper": [None] * len(prices), "middle": [None] * len(prices), "lower": [None] * len(prices)}
        
        middle_band = self._calculate_moving_average(prices, period)
        
        upper_band = []
        lower_band = []
        
        for i in range(len(prices)):
            if i < period - 1:
                upper_band.append(None)
                lower_band.append(None)
            else:
                window = prices[i - period + 1:i + 1]
                std = np.std(window)
                middle = middle_band[i]
                
                upper_band.append(middle + (std_dev * std) if middle is not None else None)
                lower_band.append(middle - (std_dev * std) if middle is not None else None)
        
        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }
    
    def _normalize_to_percentage(self, values: List[float]) -> List[float]:
        """Normalize values to percentage change from start"""
        if not values:
            return []
        
        start_value = values[0]
        if start_value == 0:
            return [0] * len(values)
        
        return [((v - start_value) / start_value) * 100 for v in values]
    
    def _calculate_correlation(self, series1: List[float], series2: List[float]) -> float:
        """Calculate correlation between two price series"""
        if len(series1) != len(series2) or len(series1) < 2:
            return 0.0
        
        correlation = np.corrcoef(series1, series2)[0, 1]
        return round(correlation, 3) if not np.isnan(correlation) else 0.0
    
    def _find_most_correlated(self, symbols: List[str], matrix: List[List[float]]) -> Dict[str, float]:
        """Find most correlated pairs"""
        max_corr = 0
        most_correlated = {}
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = matrix[i][j]
                if abs(corr) > max_corr:
                    max_corr = abs(corr)
                    most_correlated = {f"{symbols[i]}-{symbols[j]}": corr}
        
        return most_correlated
    
    def _find_least_correlated(self, symbols: List[str], matrix: List[List[float]]) -> Dict[str, float]:
        """Find least correlated pairs"""
        min_corr = 1.0
        least_correlated = {}
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = abs(matrix[i][j])
                if corr < min_corr:
                    min_corr = corr
                    least_correlated = {f"{symbols[i]}-{symbols[j]}": corr}
        
        return least_correlated
    
    def _calculate_average_correlation(self, matrix: List[List[float]]) -> float:
        """Calculate average correlation (excluding diagonal)"""
        correlations = []
        
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i != j:
                    correlations.append(abs(matrix[i][j]))
        
        return round(np.mean(correlations), 3) if correlations else 0.0
    
    def _get_sector_colors(self, sectors: List[str]) -> List[str]:
        """Get colors for sectors"""
        color_map = {
            "Technology": "#3B82F6",
            "Finance": "#10B981",
            "Healthcare": "#F59E0B",
            "Energy": "#EF4444",
            "Real Estate": "#8B5CF6",
            "Cryptocurrency": "#F97316",
            "Other": "#6B7280"
        }
        
        return [color_map.get(sector, "#6B7280") for sector in sectors]
    
    def _empty_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Return empty chart data structure"""
        return {
            "type": chart_type,
            "data": None,
            "metadata": {"message": "No data available"}
        }

# Global instance
chart_service = ChartService()
