"""
API Routes for Export Functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from services.export_service import export_service
from schemas import User
from auth import get_current_user

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/portfolio/csv")
def export_portfolio_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export portfolio data to CSV format
    """
    try:
        csv_data = export_service.export_portfolio_to_csv(current_user.id, db)
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=portfolio_{current_user.id}_{current_user.email}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals/csv")
def export_goals_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export goals data to CSV format
    """
    try:
        csv_data = export_service.export_goals_to_csv(current_user.id, db)
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=goals_{current_user.id}_{current_user.email}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/csv")
def export_transactions_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export transactions data to CSV format
    """
    try:
        csv_data = export_service.export_transactions_to_csv(
            current_user.id, db, start_date, end_date
        )
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=transactions_{current_user.id}_{current_user.email}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/csv")
def export_performance_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export performance metrics to CSV format
    """
    try:
        csv_data = export_service.export_performance_metrics_to_csv(current_user.id, db)
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=performance_{current_user.id}_{current_user.email}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/csv")
def export_recommendations_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export recommendations to CSV format
    """
    try:
        csv_data = export_service.export_recommendations_to_csv(current_user.id, db)
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=recommendations_{current_user.id}_{current_user.email}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/html")
def export_portfolio_html(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export portfolio summary as HTML (for PDF conversion)
    """
    try:
        html_data = export_service.generate_portfolio_summary_html(current_user.id, db)
        
        return Response(
            content=html_data,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=portfolio_report_{current_user.id}_{current_user.email}.html"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
