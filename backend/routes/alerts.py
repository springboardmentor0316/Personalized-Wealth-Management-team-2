from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database import get_db
from services.alert_service import alert_service
from models import User
from auth import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Pydantic models for request/response
class CreateAlertRequest(BaseModel):
    alert_type: str
    symbol: Optional[str] = None
    condition: str
    threshold_value: float
    notification_method: str = "email"
    frequency: str = "once"

class UpdateAlertRequest(BaseModel):
    alert_type: Optional[str] = None
    symbol: Optional[str] = None
    condition: Optional[str] = None
    threshold_value: Optional[float] = None
    notification_method: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/")
async def get_user_alerts(
    active_only: bool = Query(True, description="Show only active alerts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for the current user"""
    try:
        alerts = alert_service.get_user_alerts(
            current_user.id, active_only, db
        )
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "is_active": alert.is_active,
                "is_triggered": alert.is_triggered,
                "notification_method": alert.notification_method,
                "frequency": alert.frequency,
                "created_at": alert.created_at.isoformat(),
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "last_notified": alert.last_notified.isoformat() if alert.last_notified else None
            })
        
        return {
            "success": True,
            "data": {
                "alerts": alert_data,
                "total_count": len(alert_data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_alert(
    alert_data: CreateAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    try:
        alert = alert_service.create_alert(
            current_user.id, alert_data.dict(), db
        )
        
        return {
            "success": True,
            "data": {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "notification_method": alert.notification_method,
                "frequency": alert.frequency,
                "created_at": alert.created_at.isoformat(),
                "message": "Alert created successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    update_data: UpdateAlertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing alert"""
    try:
        # Filter out None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        alert = alert_service.update_alert(
            alert_id, current_user.id, update_dict, db
        )
        
        return {
            "success": True,
            "data": {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "is_active": alert.is_active,
                "notification_method": alert.notification_method,
                "frequency": alert.frequency,
                "updated_at": datetime.utcnow().isoformat(),
                "message": "Alert updated successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    try:
        success = alert_service.delete_alert(
            alert_id, current_user.id, db
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "data": {
                "message": "Alert deleted successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check")
async def check_all_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check all alerts for the current user"""
    try:
        # Get user's alerts and check them
        user_alerts = alert_service.get_user_alerts(current_user.id, True, db)
        
        triggered_alerts = []
        for alert in user_alerts:
            # Check individual alert
            if alert.alert_type == "price" and alert.symbol:
                triggered = alert_service._check_price_alerts([alert], db)
                triggered_alerts.extend(triggered)
            elif alert.alert_type == "portfolio":
                triggered = alert_service._check_portfolio_alerts([alert], db)
                triggered_alerts.extend(triggered)
            elif alert.alert_type == "goal":
                triggered = alert_service._check_goal_alerts([alert], db)
                triggered_alerts.extend(triggered)
        
        return {
            "success": True,
            "data": {
                "triggered_alerts": triggered_alerts,
                "total_triggered": len(triggered_alerts),
                "checked_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_alert_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics for the user"""
    try:
        stats = alert_service.get_alert_statistics(
            current_user.id, db
        )
        
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/smart-alerts")
async def create_smart_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create intelligent alerts based on user behavior"""
    try:
        created_alerts = alert_service.create_smart_alerts(
            current_user.id, db
        )
        
        alert_data = []
        for alert in created_alerts:
            alert_data.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "notification_method": alert.notification_method,
                "frequency": alert.frequency
            })
        
        return {
            "success": True,
            "data": {
                "created_alerts": alert_data,
                "total_created": len(alert_data),
                "message": f"Created {len(alert_data)} smart alerts based on your portfolio"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_alert_types():
    """Get available alert types and conditions"""
    try:
        alert_types = {
            "price": {
                "name": "Price Alert",
                "description": "Get notified when a stock price crosses a threshold",
                "conditions": ["above", "below", "equals"],
                "requires_symbol": True,
                "examples": [
                    {"condition": "above", "threshold": 150.0, "description": "Alert when AAPL goes above $150"},
                    {"condition": "below", "threshold": 100.0, "description": "Alert when TSLA goes below $100"}
                ]
            },
            "portfolio": {
                "name": "Portfolio Alert",
                "description": "Get notified when your portfolio value changes significantly",
                "conditions": ["above", "below"],
                "requires_symbol": False,
                "examples": [
                    {"condition": "above", "threshold": 100000.0, "description": "Alert when portfolio exceeds $100,000"},
                    {"condition": "below", "threshold": 50000.0, "description": "Alert when portfolio drops below $50,000"}
                ]
            },
            "goal": {
                "name": "Goal Alert",
                "description": "Get notified about goal progress",
                "conditions": ["above"],
                "requires_symbol": False,
                "examples": [
                    {"condition": "above", "threshold": 50.0, "description": "Alert when goal is 50% complete"},
                    {"condition": "above", "threshold": 100.0, "description": "Alert when goal is achieved"}
                ]
            },
            "market": {
                "name": "Market Alert",
                "description": "Get notified about significant market movements",
                "conditions": ["significant_move"],
                "requires_symbol": False,
                "examples": [
                    {"condition": "significant_move", "threshold": 3.0, "description": "Alert when market moves 3%"}
                ]
            }
        }
        
        notification_methods = {
            "email": {"name": "Email", "description": "Receive alerts via email"},
            "push": {"name": "Push Notification", "description": "Receive push notifications"},
            "sms": {"name": "SMS", "description": "Receive SMS alerts"}
        }
        
        frequencies = {
            "once": {"name": "Once", "description": "Alert only once when triggered"},
            "daily": {"name": "Daily", "description": "Alert daily while condition is met"},
            "weekly": {"name": "Weekly", "description": "Alert weekly while condition is met"}
        }
        
        return {
            "success": True,
            "data": {
                "alert_types": alert_types,
                "notification_methods": notification_methods,
                "frequencies": frequencies
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_alert_history(
    limit: int = Query(20, description="Number of historical alerts to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical triggered alerts"""
    try:
        from models_pkg.analytics import UserAlert
        
        alerts = db.query(UserAlert).filter(
            UserAlert.user_id == current_user.id,
            UserAlert.is_triggered == True
        ).order_by(UserAlert.triggered_at.desc()).limit(limit).all()
        
        history = []
        for alert in alerts:
            history.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "notification_method": alert.notification_method
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

@router.post("/{alert_id}/test")
async def test_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test an alert without actually triggering it"""
    try:
        from models_pkg.analytics import UserAlert
        
        alert = db.query(UserAlert).filter(
            UserAlert.id == alert_id,
            UserAlert.user_id == current_user.id
        ).first()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Test the alert condition
        current_value = None
        would_trigger = False
        
        if alert.alert_type == "price" and alert.symbol:
            from models_pkg.market import MarketPrice
            price_record = db.query(MarketPrice).filter(
                MarketPrice.symbol == alert.symbol
            ).order_by(MarketPrice.timestamp.desc()).first()
            
            if price_record:
                current_value = price_record.price
                would_trigger = alert_service._evaluate_condition(
                    current_value, alert.condition, alert.threshold_value
                )
        
        elif alert.alert_type == "portfolio":
            current_value = alert_service._get_portfolio_value(current_user.id, db)
            would_trigger = alert_service._evaluate_condition(
                current_value, alert.condition, alert.threshold_value
            )
        
        return {
            "success": True,
            "data": {
                "alert_id": alert.id,
                "current_value": current_value,
                "threshold_value": alert.threshold_value,
                "condition": alert.condition,
                "would_trigger": would_trigger,
                "message": "Alert test completed successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import datetime for use in endpoints
from datetime import datetime
