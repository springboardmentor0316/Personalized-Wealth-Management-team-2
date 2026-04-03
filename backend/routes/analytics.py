from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database import get_db
from services.analytics_service import analytics_service
from services.recommendation_service import recommendation_service
from services.alert_service import alert_service
from services.chart_service import chart_service
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/portfolio/performance")
async def get_portfolio_performance(
    timeframe: str = Query("1M", description="Timeframe: 1D, 1W, 1M, 3M, 6M, 1Y, ALL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio performance metrics and chart data"""
    try:
        # Get performance metrics
        metrics = analytics_service.calculate_performance_metrics(
            current_user.id, timeframe.lower(), db
        )
        
        # Get chart data
        chart_data = chart_service.get_portfolio_performance_chart_data(
            current_user.id, timeframe, db
        )
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "chart": chart_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/risk-metrics")
async def get_risk_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed risk metrics for portfolio"""
    try:
        # Get performance metrics for different periods
        periods = ["monthly", "quarterly", "yearly"]
        risk_data = {}
        
        for period in periods:
            metrics = analytics_service.calculate_performance_metrics(
                current_user.id, period, db
            )
            risk_data[period] = {
                "volatility": metrics["volatility"],
                "sharpe_ratio": metrics["sharpe_ratio"],
                "max_drawdown": metrics["max_drawdown"],
                "beta": metrics["beta"],
                "alpha": metrics["alpha"]
            }
        
        return {
            "success": True,
            "data": risk_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/asset-allocation")
async def get_asset_allocation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current vs target asset allocation"""
    try:
        allocation_data = analytics_service.get_asset_allocation_analysis(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": allocation_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-health")
async def get_financial_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive financial health score"""
    try:
        health_data = analytics_service.get_financial_health_score(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": health_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/snapshot")
async def create_portfolio_snapshot(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio snapshot"""
    try:
        snapshot = analytics_service.create_portfolio_snapshot(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": {
                "snapshot_id": snapshot.id,
                "total_value": snapshot.total_value,
                "created_at": snapshot.snapshot_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/history")
async def get_portfolio_history(
    days: int = Query(30, description="Number of days of history"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical portfolio snapshots"""
    try:
        from models_pkg.analytics import PortfolioSnapshot
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        snapshots = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.user_id == current_user.id,
            PortfolioSnapshot.snapshot_date >= start_date
        ).order_by(PortfolioSnapshot.snapshot_date.desc()).all()
        
        history = []
        for snapshot in snapshots:
            history.append({
                "id": snapshot.id,
                "total_value": snapshot.total_value,
                "investments_value": snapshot.investments_value,
                "cash_balance": snapshot.cash_balance,
                "asset_allocation": snapshot.asset_allocation,
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "metadata": snapshot.metadata
            })
        
        return {
            "success": True,
            "data": {
                "history": history,
                "total_snapshots": len(history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/periods")
async def get_performance_periods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance data for all time periods"""
    try:
        periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        performance_data = {}
        
        for period in periods:
            metrics = analytics_service.calculate_performance_metrics(
                current_user.id, period, db
            )
            performance_data[period] = metrics
        
        return {
            "success": True,
            "data": performance_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
