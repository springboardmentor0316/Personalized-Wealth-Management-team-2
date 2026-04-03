from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models_pkg.analytics import UserAlert
from models_pkg.market import MarketPrice
from models import User, Investment, Goal
from database import SessionLocal
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AlertService:
    """Automated alert and notification service"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.alert_types = {
            "price": self._check_price_alerts,
            "portfolio": self._check_portfolio_alerts,
            "goal": self._check_goal_alerts,
            "market": self._check_market_alerts
        }
    
    def create_alert(self, user_id: int, alert_data: Dict[str, Any], db: Session = None) -> UserAlert:
        """Create a new user alert"""
        if db is None:
            db = SessionLocal()
        
        try:
            alert = UserAlert(
                user_id=user_id,
                alert_type=alert_data["alert_type"],
                symbol=alert_data.get("symbol"),
                condition=alert_data["condition"],
                threshold_value=alert_data["threshold_value"],
                notification_method=alert_data.get("notification_method", "email"),
                frequency=alert_data.get("frequency", "once")
            )
            
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            return alert
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create alert: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_user_alerts(self, user_id: int, active_only: bool = True, db: Session = None) -> List[UserAlert]:
        """Get all alerts for a user"""
        if db is None:
            db = SessionLocal()
        
        try:
            query = db.query(UserAlert).filter(UserAlert.user_id == user_id)
            
            if active_only:
                query = query.filter(UserAlert.is_active == True)
            
            return query.order_by(desc(UserAlert.created_at)).all()
            
        except Exception as e:
            raise Exception(f"Failed to get user alerts: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def update_alert(self, alert_id: int, user_id: int, update_data: Dict[str, Any], db: Session = None) -> UserAlert:
        """Update an existing alert"""
        if db is None:
            db = SessionLocal()
        
        try:
            alert = db.query(UserAlert).filter(
                and_(UserAlert.id == alert_id, UserAlert.user_id == user_id)
            ).first()
            
            if not alert:
                raise Exception("Alert not found")
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(alert, key):
                    setattr(alert, key, value)
            
            db.commit()
            db.refresh(alert)
            
            return alert
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to update alert: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def delete_alert(self, alert_id: int, user_id: int, db: Session = None) -> bool:
        """Delete an alert"""
        if db is None:
            db = SessionLocal()
        
        try:
            alert = db.query(UserAlert).filter(
                and_(UserAlert.id == alert_id, UserAlert.user_id == user_id)
            ).first()
            
            if alert:
                db.delete(alert)
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete alert: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def check_all_alerts(self, db: Session = None) -> Dict[str, Any]:
        """Check all active alerts and trigger notifications"""
        if db is None:
            db = SessionLocal()
        
        try:
            results = {
                "price_alerts": [],
                "portfolio_alerts": [],
                "goal_alerts": [],
                "market_alerts": [],
                "total_triggered": 0
            }
            
            # Get all active alerts
            active_alerts = db.query(UserAlert).filter(
                and_(
                    UserAlert.is_active == True,
                    UserAlert.is_triggered == False
                )
            ).all()
            
            # Group alerts by type
            alerts_by_type = {}
            for alert in active_alerts:
                alert_type = alert.alert_type
                if alert_type not in alerts_by_type:
                    alerts_by_type[alert_type] = []
                alerts_by_type[alert_type].append(alert)
            
            # Check each type of alert
            for alert_type, alerts in alerts_by_type.items():
                if alert_type in self.alert_types:
                    triggered_alerts = self.alert_types[alert_type](alerts, db)
                    results[f"{alert_type}_alerts"] = triggered_alerts
                    results["total_triggered"] += len(triggered_alerts)
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to check alerts: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def _check_price_alerts(self, alerts: List[UserAlert], db: Session) -> List[Dict[str, Any]]:
        """Check price-based alerts"""
        triggered = []
        
        for alert in alerts:
            if not alert.symbol:
                continue
            
            try:
                # Get current price
                price_record = db.query(MarketPrice).filter(
                    MarketPrice.symbol == alert.symbol
                ).order_by(desc(MarketPrice.timestamp)).first()
                
                if not price_record:
                    continue
                
                current_price = price_record.price
                alert.current_value = current_price
                
                # Check condition
                triggered_condition = self._evaluate_condition(
                    current_price, alert.condition, alert.threshold_value
                )
                
                if triggered_condition:
                    # Mark alert as triggered
                    alert.is_triggered = True
                    alert.triggered_at = datetime.utcnow()
                    
                    triggered.append({
                        "alert_id": alert.id,
                        "user_id": alert.user_id,
                        "type": "price",
                        "symbol": alert.symbol,
                        "condition": alert.condition,
                        "threshold": alert.threshold_value,
                        "current_value": current_price,
                        "message": self._generate_price_alert_message(alert, current_price),
                        "notification_method": alert.notification_method
                    })
                
            except Exception as e:
                print(f"Error checking price alert {alert.id}: {str(e)}")
                continue
        
        if triggered:
            db.commit()
        
        return triggered
    
    def _check_portfolio_alerts(self, alerts: List[UserAlert], db: Session) -> List[Dict[str, Any]]:
        """Check portfolio-based alerts"""
        triggered = []
        
        for alert in alerts:
            try:
                # Get user's current portfolio value
                portfolio_value = self._get_portfolio_value(alert.user_id, db)
                alert.current_value = portfolio_value
                
                # Check condition
                triggered_condition = self._evaluate_condition(
                    portfolio_value, alert.condition, alert.threshold_value
                )
                
                if triggered_condition:
                    # Mark alert as triggered
                    alert.is_triggered = True
                    alert.triggered_at = datetime.utcnow()
                    
                    triggered.append({
                        "alert_id": alert.id,
                        "user_id": alert.user_id,
                        "type": "portfolio",
                        "condition": alert.condition,
                        "threshold": alert.threshold_value,
                        "current_value": portfolio_value,
                        "message": self._generate_portfolio_alert_message(alert, portfolio_value),
                        "notification_method": alert.notification_method
                    })
                
            except Exception as e:
                print(f"Error checking portfolio alert {alert.id}: {str(e)}")
                continue
        
        if triggered:
            db.commit()
        
        return triggered
    
    def _check_goal_alerts(self, alerts: List[UserAlert], db: Session) -> List[Dict[str, Any]]:
        """Check goal-based alerts"""
        triggered = []
        
        for alert in alerts:
            try:
                # Get user's goals
                goals = db.query(Goal).filter(Goal.user_id == alert.user_id).all()
                
                for goal in goals:
                    progress_percentage = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
                    
                    # Check if goal progress crosses threshold
                    triggered_condition = self._evaluate_condition(
                        progress_percentage, alert.condition, alert.threshold_value
                    )
                    
                    if triggered_condition:
                        # Mark alert as triggered
                        alert.is_triggered = True
                        alert.triggered_at = datetime.utcnow()
                        
                        triggered.append({
                            "alert_id": alert.id,
                            "user_id": alert.user_id,
                            "type": "goal",
                            "goal_id": goal.id,
                            "goal_name": goal.name,
                            "condition": alert.condition,
                            "threshold": alert.threshold_value,
                            "current_value": progress_percentage,
                            "message": self._generate_goal_alert_message(goal, progress_percentage),
                            "notification_method": alert.notification_method
                        })
                        break  # One trigger per alert
                
            except Exception as e:
                print(f"Error checking goal alert {alert.id}: {str(e)}")
                continue
        
        if triggered:
            db.commit()
        
        return triggered
    
    def _check_market_alerts(self, alerts: List[UserAlert], db: Session) -> List[Dict[str, Any]]:
        """Check market-wide alerts"""
        triggered = []
        
        for alert in alerts:
            try:
                # Get major market indices
                market_symbols = ["SPY", "QQQ", "DIA", "VTI"]
                market_data = {}
                
                for symbol in market_symbols:
                    price_record = db.query(MarketPrice).filter(
                        MarketPrice.symbol == symbol
                    ).order_by(desc(MarketPrice.timestamp)).first()
                    
                    if price_record:
                        # Calculate daily change (simplified)
                        market_data[symbol] = {
                            "price": price_record.price,
                            "change": np.random.uniform(-0.05, 0.05)  # Simulated change
                        }
                
                # Check if any market condition is met
                market_triggered = False
                triggered_symbol = None
                
                for symbol, data in market_data.items():
                    if abs(data["change"]) > 0.03:  # 3% move
                        market_triggered = True
                        triggered_symbol = symbol
                        break
                
                if market_triggered:
                    # Mark alert as triggered
                    alert.is_triggered = True
                    alert.triggered_at = datetime.utcnow()
                    
                    triggered.append({
                        "alert_id": alert.id,
                        "user_id": alert.user_id,
                        "type": "market",
                        "symbol": triggered_symbol,
                        "condition": "significant_move",
                        "threshold": 3.0,
                        "current_value": market_data[triggered_symbol]["change"] * 100,
                        "message": f"Market alert: {triggered_symbol} moved {market_data[triggered_symbol]['change']*100:.1f}%",
                        "notification_method": alert.notification_method
                    })
                
            except Exception as e:
                print(f"Error checking market alert {alert.id}: {str(e)}")
                continue
        
        if triggered:
            db.commit()
        
        return triggered
    
    def _evaluate_condition(self, current_value: float, condition: str, threshold: float) -> bool:
        """Evaluate if alert condition is met"""
        if condition == "above":
            return current_value > threshold
        elif condition == "below":
            return current_value < threshold
        elif condition == "equals":
            return abs(current_value - threshold) < 0.01
        elif condition == "change_percent_up":
            # This would need historical data for proper implementation
            return False
        elif condition == "change_percent_down":
            return False
        else:
            return False
    
    def _generate_price_alert_message(self, alert: UserAlert, current_price: float) -> str:
        """Generate price alert message"""
        direction = "above" if current_price > alert.threshold_value else "below"
        return f"Price Alert: {alert.symbol} is now ${current_price:.2f}, which is {direction} your threshold of ${alert.threshold_value:.2f}"
    
    def _generate_portfolio_alert_message(self, alert: UserAlert, portfolio_value: float) -> str:
        """Generate portfolio alert message"""
        direction = "above" if portfolio_value > alert.threshold_value else "below"
        return f"Portfolio Alert: Your portfolio value is ${portfolio_value:.2f}, which is {direction} your threshold of ${alert.threshold_value:.2f}"
    
    def _generate_goal_alert_message(self, goal: Goal, progress_percentage: float) -> str:
        """Generate goal alert message"""
        return f"Goal Alert: '{goal.name}' is {progress_percentage:.1f}% complete (${goal.current_amount:.2f} of ${goal.target_amount:.2f})"
    
    def _get_portfolio_value(self, user_id: int, db: Session) -> float:
        """Get current portfolio value for a user"""
        try:
            from models import Investment
            
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            total_value = 0.0
            
            for investment in investments:
                price_record = db.query(MarketPrice).filter(
                    MarketPrice.symbol == investment.symbol
                ).order_by(desc(MarketPrice.timestamp)).first()
                
                if price_record:
                    total_value += investment.quantity * price_record.price
            
            return total_value
            
        except Exception:
            return 0.0
    
    def get_alert_statistics(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Get alert statistics for a user"""
        if db is None:
            db = SessionLocal()
        
        try:
            total_alerts = db.query(UserAlert).filter(UserAlert.user_id == user_id).count()
            active_alerts = db.query(UserAlert).filter(
                and_(UserAlert.user_id == user_id, UserAlert.is_active == True)
            ).count()
            triggered_alerts = db.query(UserAlert).filter(
                and_(UserAlert.user_id == user_id, UserAlert.is_triggered == True)
            ).count()
            
            # Get alerts by type
            alerts_by_type = db.query(
                UserAlert.alert_type,
                func.count(UserAlert.id).label('count')
            ).filter(UserAlert.user_id == user_id).group_by(UserAlert.alert_type).all()
            
            type_distribution = {row.alert_type: row.count for row in alerts_by_type}
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "triggered_alerts": triggered_alerts,
                "success_rate": (triggered_alerts / total_alerts * 100) if total_alerts > 0 else 0,
                "type_distribution": type_distribution
            }
            
        except Exception as e:
            raise Exception(f"Failed to get alert statistics: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def create_smart_alerts(self, user_id: int, db: Session = None) -> List[UserAlert]:
        """Create intelligent alerts based on user behavior"""
        if db is None:
            db = SessionLocal()
        
        try:
            created_alerts = []
            
            # Get user's portfolio and goals
            portfolio_value = self._get_portfolio_value(user_id, db)
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            # Portfolio value alerts
            if portfolio_value > 0:
                # 10% decline alert
                decline_alert = UserAlert(
                    user_id=user_id,
                    alert_type="portfolio",
                    condition="below",
                    threshold_value=portfolio_value * 0.9,
                    notification_method="email",
                    frequency="once"
                )
                created_alerts.append(decline_alert)
                
                # 20% growth alert
                growth_alert = UserAlert(
                    user_id=user_id,
                    alert_type="portfolio",
                    condition="above",
                    threshold_value=portfolio_value * 1.2,
                    notification_method="email",
                    frequency="once"
                )
                created_alerts.append(growth_alert)
            
            # Goal progress alerts
            for goal in goals:
                if goal.target_amount > 0:
                    # 50% progress alert
                    progress_alert = UserAlert(
                        user_id=user_id,
                        alert_type="goal",
                        condition="above",
                        threshold_value=50.0,
                        notification_method="email",
                        frequency="once"
                    )
                    created_alerts.append(progress_alert)
            
            # Price alerts for major holdings
            for investment in investments:
                if investment.quantity * 100 > portfolio_value * 0.1:  # >10% of portfolio
                    price_record = db.query(MarketPrice).filter(
                        MarketPrice.symbol == investment.symbol
                    ).order_by(desc(MarketPrice.timestamp)).first()
                    
                    if price_record:
                        # 15% price change alert
                        price_alert = UserAlert(
                            user_id=user_id,
                            alert_type="price",
                            symbol=investment.symbol,
                            condition="above",
                            threshold_value=price_record.price * 1.15,
                            notification_method="email",
                            frequency="once"
                        )
                        created_alerts.append(price_alert)
            
            # Save all alerts
            for alert in created_alerts:
                db.add(alert)
            
            db.commit()
            return created_alerts
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create smart alerts: {str(e)}")
        finally:
            if db is None:
                db.close()

# Global instance
alert_service = AlertService()
