from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database import get_db
from services.chart_service import chart_service
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/charts", tags=["charts"])

@router.get("/portfolio/performance")
async def get_portfolio_performance_chart(
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance chart data"""
    try:
        chart_data = chart_service.get_portfolio_performance_chart_data(
            current_user.id, timeframe, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/asset-allocation")
async def get_asset_allocation_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get asset allocation pie chart data"""
    try:
        chart_data = chart_service.get_asset_allocation_chart_data(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}")
async def get_stock_price_chart(
    symbol: str,
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stock price chart with technical indicators"""
    try:
        chart_data = chart_service.get_stock_price_chart_data(
            symbol.upper(), timeframe, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-comparison")
async def get_performance_comparison_chart(
    benchmarks: str = Query("SPY,QQQ", description="Comma-separated benchmark symbols"),
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance comparison with benchmarks"""
    try:
        benchmark_symbols = [s.strip().upper() for s in benchmarks.split(",")]
        
        chart_data = chart_service.get_performance_comparison_chart_data(
            current_user.id, benchmark_symbols, timeframe, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-return-scatter")
async def get_risk_return_scatter_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk-return scatter plot data"""
    try:
        chart_data = chart_service.get_risk_return_scatter_data(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation-heatmap")
async def get_correlation_heatmap_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get correlation heatmap for portfolio holdings"""
    try:
        chart_data = chart_service.get_correlation_heatmap_data(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-performance")
async def get_sector_performance_chart(
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sector performance chart data"""
    try:
        # Get sector ETFs for comparison
        sector_etfs = {
            "Technology": "XLK",
            "Finance": "XLF",
            "Healthcare": "XLV",
            "Energy": "XLE",
            "Real Estate": "XLRE",
            "Utilities": "XLU",
            "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP",
            "Materials": "XLB",
            "Industrial": "XLI"
        }
        
        sector_data = {}
        
        for sector, symbol in sector_etfs.items():
            try:
                chart_data = chart_service.get_stock_price_chart_data(
                    symbol, timeframe, db
                )
                
                if chart_data["data"] and chart_data["data"]["ohlc"]:
                    closes = [item["close"] for item in chart_data["data"]["ohlc"]]
                    dates = [item["date"] for item in chart_data["data"]["ohlc"]]
                    
                    # Calculate percentage return
                    if closes and len(closes) > 1:
                        total_return = ((closes[-1] - closes[0]) / closes[0]) * 100
                        sector_data[sector] = {
                            "symbol": symbol,
                            "return": round(total_return, 2),
                            "current_price": closes[-1],
                            "data_points": len(closes)
                        }
            except Exception:
                continue
        
        # Sort by return
        sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]["return"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "sectors": dict(sorted_sectors),
                "timeframe": timeframe,
                "total_sectors": len(sector_data),
                "best_performer": sorted_sectors[0] if sorted_sectors else None,
                "worst_performer": sorted_sectors[-1] if sorted_sectors else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio-composition")
async def get_portfolio_composition_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed portfolio composition chart"""
    try:
        from models import Investment
        from models_pkg.market import MarketPrice
        
        # Get user's investments
        investments = db.query(Investment).filter(
            Investment.user_id == current_user.id
        ).all()
        
        composition_data = []
        total_value = 0.0
        
        for investment in investments:
            # Get current price
            price_record = db.query(MarketPrice).filter(
                MarketPrice.symbol == investment.symbol
            ).order_by(MarketPrice.timestamp.desc()).first()
            
            if price_record:
                current_value = investment.quantity * price_record.price
                total_value += current_value
                
                composition_data.append({
                    "symbol": investment.symbol,
                    "quantity": investment.quantity,
                    "current_price": price_record.price,
                    "value": current_value,
                    "weight": 0,  # Will be calculated below
                    "average_cost": investment.average_cost,
                    "gain_loss": current_value - (investment.quantity * investment.average_cost),
                    "gain_loss_percent": ((current_value - (investment.quantity * investment.average_cost)) / (investment.quantity * investment.average_cost) * 100) if investment.average_cost > 0 else 0
                })
        
        # Calculate weights
        if total_value > 0:
            for item in composition_data:
                item["weight"] = (item["value"] / total_value) * 100
        
        # Sort by weight
        composition_data.sort(key=lambda x: x["weight"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "holdings": composition_data,
                "total_value": total_value,
                "total_holdings": len(composition_data),
                "top_10_holdings": composition_data[:10],
                "metadata": {
                    "largest_holding": composition_data[0] if composition_data else None,
                    "concentration_ratio": composition_data[0]["weight"] if composition_data else 0,
                    "total_gain_loss": sum(item["gain_loss"] for item in composition_data)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drawdown-chart")
async def get_drawdown_chart(
    timeframe: str = Query("1Y", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio drawdown chart data"""
    try:
        # Get portfolio performance data
        perf_data = chart_service.get_portfolio_performance_chart_data(
            current_user.id, timeframe, db
        )
        
        if not perf_data["data"] or not perf_data["data"]["values"]:
            return {
                "success": True,
                "data": {"message": "No data available for drawdown analysis"}
            }
        
        values = perf_data["data"]["values"]
        dates = perf_data["data"]["dates"]
        
        # Calculate drawdown
        peak = values[0]
        drawdowns = []
        
        for i, value in enumerate(values):
            if value > peak:
                peak = value
            
            drawdown = ((peak - value) / peak) * 100
            drawdowns.append({
                "date": dates[i],
                "portfolio_value": value,
                "peak": peak,
                "drawdown": drawdown
            })
        
        # Find maximum drawdown
        max_dd = max(drawdowns, key=lambda x: x["drawdown"]) if drawdowns else None
        
        return {
            "success": True,
            "data": {
                "drawdowns": drawdowns,
                "max_drawdown": max_dd,
                "current_drawdown": drawdowns[-1]["drawdown"] if drawdowns else 0,
                "timeframe": timeframe
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/volatility-chart")
async def get_volatility_chart(
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    window: int = Query(20, description="Volatility calculation window"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get rolling volatility chart data"""
    try:
        # Get portfolio performance data
        perf_data = chart_service.get_portfolio_performance_chart_data(
            current_user.id, timeframe, db
        )
        
        if not perf_data["data"] or not perf_data["data"]["values"]:
            return {
                "success": True,
                "data": {"message": "No data available for volatility analysis"}
            }
        
        values = perf_data["data"]["values"]
        dates = perf_data["data"]["dates"]
        
        # Calculate rolling volatility
        volatility_data = []
        
        for i in range(len(values)):
            if i < window - 1:
                volatility_data.append({
                    "date": dates[i],
                    "volatility": None
                })
            else:
                window_values = values[i - window + 1:i + 1]
                returns = []
                
                for j in range(1, len(window_values)):
                    ret = (window_values[j] - window_values[j-1]) / window_values[j-1]
                    returns.append(ret)
                
                if returns:
                    volatility = (np.std(returns) * np.sqrt(252)) * 100  # Annualized volatility in percentage
                    volatility_data.append({
                        "date": dates[i],
                        "volatility": round(volatility, 2)
                    })
                else:
                    volatility_data.append({
                        "date": dates[i],
                        "volatility": None
                    })
        
        # Calculate average volatility
        valid_volatilities = [v["volatility"] for v in volatility_data if v["volatility"] is not None]
        avg_volatility = np.mean(valid_volatilities) if valid_volatilities else 0
        
        return {
            "success": True,
            "data": {
                "volatility": volatility_data,
                "average_volatility": round(avg_volatility, 2),
                "current_volatility": valid_volatilities[-1] if valid_volatilities else 0,
                "window": window,
                "timeframe": timeframe
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-summary")
async def get_dashboard_chart_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary data for dashboard charts"""
    try:
        # Get multiple chart data points for dashboard
        portfolio_perf = chart_service.get_portfolio_performance_chart_data(
            current_user.id, "1M", db
        )
        
        asset_alloc = chart_service.get_asset_allocation_chart_data(
            current_user.id, db
        )
        
        risk_return = chart_service.get_risk_return_scatter_data(
            current_user.id, db
        )
        
        # Calculate summary metrics
        summary = {
            "portfolio_performance": {
                "current_value": portfolio_perf["data"]["metadata"]["end_value"] if portfolio_perf["data"] else 0,
                "total_return": portfolio_perf["data"]["metadata"]["total_return"] if portfolio_perf["data"] else 0,
                "volatility": portfolio_perf["data"]["metadata"]["volatility"] if portfolio_perf["data"] else 0
            },
            "asset_allocation": {
                "number_of_sectors": asset_alloc["data"]["metadata"]["number_of_sectors"] if asset_alloc["data"] else 0,
                "largest_sector": asset_alloc["data"]["metadata"]["largest_sector"] if asset_alloc["data"] else None,
                "concentration_ratio": asset_alloc["data"]["metadata"]["concentration_ratio"] if asset_alloc["data"] else 0
            },
            "risk_metrics": {
                "best_period": risk_return["data"]["metadata"]["best_period"] if risk_return["data"] else None,
                "average_return": risk_return["data"]["metadata"]["average_return"] if risk_return["data"] else 0,
                "average_risk": risk_return["data"]["metadata"]["average_risk"] if risk_return["data"] else 0
            }
        }
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import numpy for calculations
import numpy as np
