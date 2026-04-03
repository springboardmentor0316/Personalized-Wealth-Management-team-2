from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from database import get_db
from services.recommendation_service import recommendation_service
from services.analytics_service import analytics_service
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("/portfolio")
async def get_portfolio_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered portfolio recommendations"""
    try:
        recommendations = recommendation_service.generate_portfolio_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        import traceback
        print(f"Portfolio recommendations error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rebalancing")
async def get_rebalancing_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific rebalancing recommendations"""
    try:
        rebalancing = recommendation_service.generate_rebalancing_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": rebalancing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tax-optimization")
async def get_tax_optimization_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tax optimization recommendations"""
    try:
        tax_recommendations = recommendation_service.generate_tax_optimization_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": tax_recommendations,
                "total_count": len(tax_recommendations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/goal-based")
async def get_goal_based_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal-based investment recommendations"""
    try:
        goal_recommendations = recommendation_service.generate_goal_based_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": goal_recommendations,
                "total_count": len(goal_recommendations)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all types of recommendations"""
    try:
        # Get all recommendation types
        portfolio_recs = recommendation_service.generate_portfolio_recommendations(
            current_user.id, db
        )
        rebalancing_rec = recommendation_service.generate_rebalancing_recommendations(
            current_user.id, db
        )
        tax_recs = recommendation_service.generate_tax_optimization_recommendations(
            current_user.id, db
        )
        goal_recs = recommendation_service.generate_goal_based_recommendations(
            current_user.id, db
        )
        
        all_recommendations = {
            "portfolio": portfolio_recs,
            "rebalancing": rebalancing_rec,
            "tax_optimization": tax_recs,
            "goal_based": goal_recs
        }
        
        # Count total recommendations
        total_count = (
            len(portfolio_recs) + 
            (1 if rebalancing_rec and "error" not in rebalancing_rec else 0) +
            len(tax_recs) + 
            len(goal_recs)
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": all_recommendations,
                "total_count": total_count,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_fresh_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate fresh recommendations (force refresh)"""
    try:
        # Clear existing recommendations for this user
        from models_pkg.analytics import Recommendation
        
        db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id
        ).delete()
        
        db.commit()
        
        # Generate new recommendations
        recommendations = recommendation_service.generate_portfolio_recommendations(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": {
                "message": "Fresh recommendations generated successfully",
                "recommendations": recommendations,
                "total_count": len(recommendations)
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_recommendation_history(
    limit: int = Query(10, description="Number of historical recommendations to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical recommendations"""
    try:
        from models_pkg.analytics import Recommendation
        
        recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == current_user.id
        ).order_by(Recommendation.created_at.desc()).limit(limit).all()
        
        history = []
        for rec in recommendations:
            history.append({
                "id": rec.id,
                "type": rec.recommendation_type,
                "title": rec.title,
                "description": rec.description,
                "status": rec.status,
                "confidence_score": rec.confidence_score,
                "created_at": rec.created_at.isoformat(),
                "expires_at": rec.expires_at.isoformat() if rec.expires_at else None,
                "implemented_at": rec.implemented_at.isoformat() if rec.implemented_at else None
            })
        
        return {
            "success": True,
            "data": {
                "history": history,
                "total_count": len(history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{recommendation_id}/status")
async def update_recommendation_status(
    recommendation_id: int,
    status: str,  # "accepted", "rejected", "implemented"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update recommendation status"""
    try:
        from models_pkg.analytics import Recommendation
        
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == current_user.id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        recommendation.status = status
        
        if status == "implemented":
            recommendation.implemented_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": f"Recommendation status updated to {status}",
                "recommendation_id": recommendation.id,
                "status": recommendation.status
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_market_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get market insights and analysis"""
    try:
        from models_pkg.analytics import MarketInsight
        
        # Get recent market insights
        insights = db.query(MarketInsight).filter(
            MarketInsight.expires_at > datetime.utcnow()
        ).order_by(MarketInsight.created_at.desc()).limit(10).all()
        
        insight_data = []
        for insight in insights:
            insight_data.append({
                "id": insight.id,
                "type": insight.insight_type,
                "title": insight.title,
                "content": insight.content,
                "sentiment_score": insight.sentiment_score,
                "trend_direction": insight.trend_direction,
                "confidence": insight.confidence,
                "impact_level": insight.impact_level,
                "symbols": insight.symbols,
                "sectors": insight.sectors,
                "created_at": insight.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "insights": insight_data,
                "total_count": len(insight_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import datetime for use in endpoints
from datetime import datetime
