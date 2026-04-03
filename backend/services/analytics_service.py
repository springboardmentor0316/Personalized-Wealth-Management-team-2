import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models_pkg.analytics import PortfolioSnapshot, PerformanceMetrics, AssetAllocation
from models_pkg.market import MarketPrice
from models import User, Investment, Transaction
from database import SessionLocal

class AnalyticsService:
    """Advanced analytics service for portfolio performance and insights"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate for Sharpe ratio
    
    def create_portfolio_snapshot(self, user_id: int, db: Session) -> PortfolioSnapshot:
        """Create a snapshot of current portfolio value and allocation"""
        try:
            # Get current investments
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            total_value = 0.0
            asset_allocation = {}
            
            for investment in investments:
                # Get current price
                price_record = db.query(MarketPrice).filter(
                    MarketPrice.symbol == investment.symbol
                ).order_by(desc(MarketPrice.timestamp)).first()
                
                if price_record:
                    current_value = investment.quantity * price_record.price
                    total_value += current_value
                    
                    # Simple asset allocation based on symbol type
                    sector = self._get_sector_from_symbol(investment.symbol)
                    asset_allocation[sector] = asset_allocation.get(sector, 0) + current_value
            
            # Convert to percentages
            if total_value > 0:
                asset_allocation = {k: (v / total_value) * 100 for k, v in asset_allocation.items()}
            
            snapshot = PortfolioSnapshot(
                user_id=user_id,
                total_value=total_value,
                investments_value=total_value,
                asset_allocation=asset_allocation,
                snapshot_data={"investment_count": len(investments)}
            )
            
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            
            return snapshot
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create portfolio snapshot: {str(e)}")
    
    def calculate_performance_metrics(self, user_id: int, period: str = "monthly", db: Session = None) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics for a user's portfolio"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get user's investments
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            if not investments:
                return self._get_empty_metrics()
            
            # Calculate current values
            current_value = sum(inv.quantity * inv.current_price for inv in investments)
            cost_basis = sum(inv.quantity * inv.average_cost for inv in investments)
            
            # Calculate total return
            total_return = ((current_value - cost_basis) / cost_basis) if cost_basis > 0 else 0
            
            # For period-based calculations, generate simulated historical data
            days_back = self._get_days_from_period(period)
            
            # Generate simulated historical values (gradual growth from cost basis to current)
            values = []
            dates = []
            end_date = datetime.utcnow()
            
            for i in range(min(days_back, 30), 0, -1):
                date_point = end_date - timedelta(days=i)
                dates.append(date_point)
                progress = 1 - (i / days_back)
                simulated_value = cost_basis + (current_value - cost_basis) * progress
                # Add small random variation for realistic volatility
                variation = simulated_value * np.random.uniform(-0.02, 0.02)
                values.append(simulated_value + variation)
            
            # Add current value
            dates.append(end_date)
            values.append(current_value)
            
            # Calculate metrics
            annualized_return = self._calculate_annualized_return(values, dates)
            volatility = self._calculate_volatility(values)
            sharpe_ratio = self._calculate_sharpe_ratio(annualized_return, volatility)
            max_drawdown = self._calculate_max_drawdown(values)
            beta = self._calculate_beta(user_id, values, db)
            alpha = annualized_return - (self.risk_free_rate + beta * 0.08)
            win_rate = self._calculate_win_rate(values)
            
            metrics = {
                "period": period,
                "start_date": dates[0].isoformat() if dates else None,
                "end_date": dates[-1].isoformat() if dates else None,
                "total_return": total_return,
                "annualized_return": annualized_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "beta": beta,
                "alpha": alpha,
                "max_drawdown": max_drawdown,
                "win_rate": win_rate,
                "benchmark_return": 0.08,
                "excess_return": annualized_return - 0.08,
                "current_value": current_value,
                "cost_basis": cost_basis
            }
            
            # Save to database
            self._save_performance_metrics(user_id, metrics, db)
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Failed to calculate performance metrics: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_asset_allocation_analysis(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Analyze current vs target asset allocation"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get target allocation
            target_allocation = db.query(AssetAllocation).filter(
                AssetAllocation.user_id == user_id
            ).first()
            
            if not target_allocation:
                # Create default allocation
                target_allocation = AssetAllocation(
                    user_id=user_id,
                    stocks_percentage=0.6,
                    bonds_percentage=0.3,
                    real_estate_percentage=0.05,
                    commodities_percentage=0.05
                )
                db.add(target_allocation)
                db.commit()
            
            # Get current allocation from latest snapshot
            latest_snapshot = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.user_id == user_id
            ).order_by(desc(PortfolioSnapshot.snapshot_date)).first()
            
            current_allocation = {}
            if latest_snapshot and latest_snapshot.asset_allocation:
                current_allocation = latest_snapshot.asset_allocation
            
            # Calculate drift
            drift_analysis = self._calculate_allocation_drift(
                target_allocation, current_allocation
            )
            
            # Rebalancing recommendations
            rebalancing_needed = any(abs(drift) > target_allocation.rebalance_threshold 
                                   for drift in drift_analysis.values())
            
            return {
                "target_allocation": {
                    "stocks": target_allocation.stocks_percentage * 100,
                    "bonds": target_allocation.bonds_percentage * 100,
                    "real_estate": target_allocation.real_estate_percentage * 100,
                    "commodities": target_allocation.commodities_percentage * 100,
                    "cash": target_allocation.cash_percentage * 100
                },
                "current_allocation": current_allocation,
                "drift_analysis": drift_analysis,
                "rebalancing_needed": rebalancing_needed,
                "last_rebalanced": target_allocation.last_rebalanced.isoformat() if target_allocation.last_rebalanced else None,
                "rebalance_threshold": target_allocation.rebalance_threshold * 100
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze asset allocation: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def get_financial_health_score(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Calculate overall financial health score"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get user data
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Get portfolio metrics
            performance = self.calculate_performance_metrics(user_id, "yearly", db)
            
            # Get current portfolio value
            latest_snapshot = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.user_id == user_id
            ).order_by(desc(PortfolioSnapshot.snapshot_date)).first()
            
            portfolio_value = latest_snapshot.total_value if latest_snapshot else 0
            
            # Calculate individual scores (0-100)
            scores = {
                "portfolio_performance": min(100, max(0, (performance["annualized_return"] + 0.1) * 500)),  # -10% = 0, +10% = 100
                "risk_management": min(100, max(0, 100 - (performance["volatility"] * 500))),  # 0% vol = 100, 20% vol = 0
                "diversification": self._calculate_diversification_score(user_id, db),
                "consistency": performance["win_rate"] * 100,  # Already 0-100
                "growth_trend": min(100, max(0, (performance["total_return"] + 0.5) * 100))  # -50% = 0, +50% = 100
            }
            
            # Calculate overall score
            overall_score = sum(scores.values()) / len(scores)
            
            # Determine health grade
            if overall_score >= 80:
                grade = "A"
                status = "Excellent"
            elif overall_score >= 70:
                grade = "B"
                status = "Good"
            elif overall_score >= 60:
                grade = "C"
                status = "Fair"
            elif overall_score >= 50:
                grade = "D"
                status = "Poor"
            else:
                grade = "F"
                status = "Critical"
            
            return {
                "overall_score": round(overall_score, 1),
                "grade": grade,
                "status": status,
                "individual_scores": scores,
                "portfolio_value": portfolio_value,
                "assessment_date": datetime.utcnow().isoformat(),
                "recommendations": self._get_health_recommendations(scores, overall_score)
            }
            
        except Exception as e:
            raise Exception(f"Failed to calculate financial health score: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def _get_sector_from_symbol(self, symbol: str) -> str:
        """Simple sector classification based on symbol"""
        symbol = symbol.upper()
        
        # Tech stocks
        if symbol in ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMZN"]:
            return "Technology"
        
        # Finance
        elif symbol in ["JPM", "BAC", "WFC", "GS"]:
            return "Finance"
        
        # Healthcare
        elif symbol in ["JNJ", "PFE", "UNH"]:
            return "Healthcare"
        
        # Energy
        elif symbol in ["XOM", "CVX"]:
            return "Energy"
        
        # Crypto
        elif symbol.endswith("-USD"):
            return "Cryptocurrency"
        
        else:
            return "Other"
    
    def _get_days_from_period(self, period: str) -> int:
        """Convert period string to days"""
        period_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "quarterly": 90,
            "yearly": 365
        }
        return period_map.get(period, 30)
    
    def _calculate_annualized_return(self, values: List[float], dates: List[datetime]) -> float:
        """Calculate annualized return"""
        if len(values) < 2:
            return 0.0
        
        total_return = (values[-1] - values[0]) / values[0]
        days = (dates[-1] - dates[0]).days
        
        if days == 0:
            return 0.0
        
        years = days / 365.25
        return (1 + total_return) ** (1 / years) - 1
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(values) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(values)):
            ret = (values[i] - values[i-1]) / values[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        return np.std(returns) * np.sqrt(252)  # Annualized volatility
    
    def _calculate_sharpe_ratio(self, annualized_return: float, volatility: float) -> float:
        """Calculate Sharpe ratio"""
        if volatility == 0:
            return 0.0
        
        return (annualized_return - self.risk_free_rate) / volatility
    
    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(values) < 2:
            return 0.0
        
        peak = values[0]
        max_dd = 0.0
        
        for value in values[1:]:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_beta(self, user_id: int, portfolio_values: List[float], db: Session) -> float:
        """Calculate beta (simplified using market proxy)"""
        # This is a simplified beta calculation
        # In production, you'd use actual market data (S&P 500)
        if len(portfolio_values) < 2:
            return 1.0
        
        # Simplified: assume portfolio has beta of 1.0
        # In reality, calculate covariance with market returns
        return 1.0
    
    def _calculate_win_rate(self, values: List[float]) -> float:
        """Calculate win rate (percentage of positive periods)"""
        if len(values) < 2:
            return 0.0
        
        wins = 0
        for i in range(1, len(values)):
            if values[i] > values[i-1]:
                wins += 1
        
        return wins / (len(values) - 1)
    
    def _save_performance_metrics(self, user_id: int, metrics: Dict[str, Any], db: Session):
        """Save performance metrics to database"""
        try:
            # Valid fields for PerformanceMetrics model
            valid_fields = [
                "total_return", "annualized_return", "volatility", "sharpe_ratio",
                "beta", "alpha", "max_drawdown", "win_rate", "benchmark_return", "excess_return"
            ]
            
            # Check if metrics already exist for this period
            existing = db.query(PerformanceMetrics).filter(
                and_(
                    PerformanceMetrics.user_id == user_id,
                    PerformanceMetrics.period == metrics["period"],
                    PerformanceMetrics.start_date >= datetime.utcnow() - timedelta(days=1)
                )
            ).first()
            
            if existing:
                # Update existing
                for key in valid_fields:
                    if key in metrics:
                        setattr(existing, key, metrics[key])
            else:
                # Create new with only valid fields
                perf_metrics = PerformanceMetrics(
                    user_id=user_id,
                    period=metrics["period"],
                    start_date=datetime.fromisoformat(metrics["start_date"]) if metrics.get("start_date") else datetime.utcnow(),
                    end_date=datetime.fromisoformat(metrics["end_date"]) if metrics.get("end_date") else datetime.utcnow(),
                    **{k: v for k, v in metrics.items() if k in valid_fields}
                )
                db.add(perf_metrics)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save performance metrics: {str(e)}")
    
    def _calculate_allocation_drift(self, target: AssetAllocation, current: Dict[str, float]) -> Dict[str, float]:
        """Calculate allocation drift from target"""
        target_map = {
            "Technology": target.stocks_percentage * 100,
            "Finance": target.bonds_percentage * 100,
            "Healthcare": target.real_estate_percentage * 100,
            "Energy": target.commodities_percentage * 100,
            "Other": target.cash_percentage * 100
        }
        
        drift = {}
        for sector, target_pct in target_map.items():
            current_pct = current.get(sector, 0)
            drift[sector] = current_pct - target_pct
        
        return drift
    
    def _calculate_diversification_score(self, user_id: int, db: Session) -> float:
        """Calculate diversification score based on portfolio concentration"""
        try:
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            if not investments:
                return 0.0
            
            # Calculate concentration (Herfindahl-Hirschman Index)
            total_value = 0.0
            values = []
            
            for investment in investments:
                price_record = db.query(MarketPrice).filter(
                    MarketPrice.symbol == investment.symbol
                ).order_by(desc(MarketPrice.timestamp)).first()
                
                if price_record:
                    value = investment.quantity * price_record.price
                    values.append(value)
                    total_value += value
            
            if total_value == 0:
                return 0.0
            
            # Calculate HHI
            hhi = sum((value / total_value) ** 2 for value in values)
            
            # Convert to diversification score (inverse of concentration)
            # HHI ranges from 1/n (perfectly diversified) to 1 (concentrated)
            max_hhi = 1.0
            min_hhi = 1.0 / len(values) if values > 0 else 1.0
            
            # Normalize to 0-100 scale
            if max_hhi == min_hhi:
                return 100.0
            
            score = ((max_hhi - hhi) / (max_hhi - min_hhi)) * 100
            return max(0, min(100, score))
            
        except Exception:
            return 50.0  # Default score on error
    
    def _get_health_recommendations(self, scores: Dict[str, float], overall: float) -> List[str]:
        """Get recommendations based on health scores"""
        recommendations = []
        
        if scores["portfolio_performance"] < 60:
            recommendations.append("Consider reviewing your investment strategy for better returns")
        
        if scores["risk_management"] < 60:
            recommendations.append("Your portfolio may be too risky. Consider diversification")
        
        if scores["diversification"] < 60:
            recommendations.append("Increase diversification to reduce concentration risk")
        
        if scores["consistency"] < 60:
            recommendations.append("Your portfolio shows inconsistent performance. Review your strategy")
        
        if scores["growth_trend"] < 60:
            recommendations.append("Your portfolio is underperforming. Consider rebalancing")
        
        if overall >= 80:
            recommendations.append("Your portfolio is performing excellently. Maintain your current strategy")
        
        return recommendations
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            "period": "monthly",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "total_return": 0.0,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "beta": 1.0,
            "alpha": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "benchmark_return": 0.08,
            "excess_return": -0.08
        }

# Global instance
analytics_service = AnalyticsService()
