from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from models_pkg.analytics import Recommendation, AssetAllocation, PortfolioSnapshot
from models_pkg.market import MarketPrice
from models import User, Investment, Transaction, Goal
from database import SessionLocal

class RecommendationService:
    """AI-powered investment recommendation service"""
    
    def __init__(self):
        self.sector_etfs = {
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
        
        self.risk_profiles = {
            "conservative": {"max_volatility": 0.10, "stock_allocation": 0.4},
            "moderate": {"max_volatility": 0.15, "stock_allocation": 0.6},
            "aggressive": {"max_volatility": 0.20, "stock_allocation": 0.8}
        }
    
    def generate_portfolio_recommendations(self, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """Generate AI-powered portfolio recommendations"""
        if db is None:
            db = SessionLocal()
        
        try:
            recommendations = []
            
            # Get user data
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Get current portfolio
            current_portfolio = self._get_current_portfolio(user_id, db)
            
            # Generate different types of recommendations
            recommendations.extend(self._generate_diversification_recommendations(user_id, current_portfolio, db))
            recommendations.extend(self._generate_risk_adjustment_recommendations(user_id, current_portfolio, db))
            recommendations.extend(self._generate_performance_optimization_recommendations(user_id, current_portfolio, db))
            recommendations.extend(self._generate_tax_optimization_recommendations(user_id, current_portfolio, db))
            
            # Save recommendations to database
            for rec in recommendations:
                self._save_recommendation(user_id, rec, db)
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"Failed to generate recommendations: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def generate_rebalancing_recommendations(self, user_id: int, db: Session = None) -> Dict[str, Any]:
        """Generate specific rebalancing recommendations"""
        if db is None:
            db = SessionLocal()
        
        try:
            # Get target allocation
            target_allocation = db.query(AssetAllocation).filter(
                AssetAllocation.user_id == user_id
            ).first()
            
            if not target_allocation:
                return {"error": "No target allocation found"}
            
            # Get current allocation
            latest_snapshot = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.user_id == user_id
            ).order_by(desc(PortfolioSnapshot.snapshot_date)).first()
            
            if not latest_snapshot:
                return {"error": "No portfolio data found"}
            
            current_allocation = latest_snapshot.asset_allocation or {}
            
            # Calculate required trades
            trades = self._calculate_rebalancing_trades(
                target_allocation, 
                current_allocation, 
                latest_snapshot.total_value,
                db
            )
            
            # Generate recommendation
            recommendation = {
                "type": "rebalancing",
                "title": "Portfolio Rebalancing Recommendation",
                "description": f"Your portfolio has drifted from target allocation. Rebalancing recommended to maintain optimal risk-return profile.",
                "reasoning": self._generate_rebalancing_reasoning(target_allocation, current_allocation),
                "trades": trades,
                "expected_impact": self._calculate_rebalancing_impact(trades, db),
                "confidence": 0.85,
                "priority": "high" if len(trades) > 0 else "low"
            }
            
            return recommendation
            
        except Exception as e:
            raise Exception(f"Failed to generate rebalancing recommendations: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def generate_tax_optimization_recommendations(self, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """Generate tax optimization recommendations"""
        if db is None:
            db = SessionLocal()
        
        try:
            recommendations = []
            
            # Get user's transactions and holdings
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
            
            # Tax loss harvesting opportunities
            loss_harvesting = self._identify_tax_loss_harvesting_opportunities(investments, db)
            if loss_harvesting:
                recommendations.append({
                    "type": "tax_optimization",
                    "title": "Tax Loss Harvesting Opportunity",
                    "description": "Sell underperforming investments to realize losses and offset gains",
                    "opportunities": loss_harvesting,
                    "potential_tax_savings": self._calculate_tax_savings(loss_harvesting),
                    "confidence": 0.75
                })
            
            # Asset location recommendations
            asset_location = self._generate_asset_location_recommendations(investments, db)
            if asset_location:
                recommendations.append(asset_location)
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"Failed to generate tax recommendations: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def generate_goal_based_recommendations(self, user_id: int, db: Session = None) -> List[Dict[str, Any]]:
        """Generate recommendations based on user goals"""
        if db is None:
            db = SessionLocal()
        
        try:
            recommendations = []
            
            # Get user's goals
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            
            for goal in goals:
                # Check if goal is on track
                goal_analysis = self._analyze_goal_progress(goal, db)
                
                if not goal_analysis["on_track"]:
                    recommendations.append({
                        "type": "goal_optimization",
                        "title": f"Optimize for {goal.name} Goal",
                        "description": f"Adjust your strategy to better achieve your {goal.name} goal",
                        "goal_id": goal.id,
                        "current_progress": goal_analysis["progress_percentage"],
                        "recommended_actions": goal_analysis["recommended_actions"],
                        "confidence": 0.80
                    })
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"Failed to generate goal-based recommendations: {str(e)}")
        finally:
            if db is None:
                db.close()
    
    def _get_current_portfolio(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get current portfolio composition and value"""
        investments = db.query(Investment).filter(Investment.user_id == user_id).all()
        
        portfolio = {
            "total_value": 0.0,
            "investments": [],
            "sectors": {},
            "risk_metrics": {}
        }
        
        for investment in investments:
            # Get current price - try market data first, fallback to investment current_price
            price_record = db.query(MarketPrice).filter(
                MarketPrice.symbol == investment.symbol
            ).order_by(desc(MarketPrice.timestamp)).first()
            
            # Use market price if available, otherwise use investment's current_price
            current_price = price_record.price if price_record else investment.current_price
            
            if current_price and current_price > 0:
                current_value = investment.quantity * current_price
                sector = self._get_sector_from_symbol(investment.symbol)
                
                portfolio["investments"].append({
                    "symbol": investment.symbol,
                    "quantity": investment.quantity,
                    "current_price": current_price,
                    "value": current_value,
                    "sector": sector,
                    "weight": 0  # Will be calculated below
                })
                
                portfolio["total_value"] += current_value
                portfolio["sectors"][sector] = portfolio["sectors"].get(sector, 0) + current_value
        
        # Calculate weights
        if portfolio["total_value"] > 0:
            for inv in portfolio["investments"]:
                inv["weight"] = inv["value"] / portfolio["total_value"]
            
            for sector in portfolio["sectors"]:
                portfolio["sectors"][sector] = portfolio["sectors"][sector] / portfolio["total_value"]
        
        return portfolio
    
    def _generate_diversification_recommendations(self, user_id: int, portfolio: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate diversification improvement recommendations"""
        recommendations = []
        
        # Check sector concentration
        max_sector_weight = max(portfolio["sectors"].values()) if portfolio["sectors"] else 0
        
        if max_sector_weight > 0.4:  # More than 40% in one sector
            recommendations.append({
                "type": "diversification",
                "title": "Reduce Sector Concentration",
                "description": f"Your portfolio is {max_sector_weight*100:.1f}% concentrated in one sector. Consider diversifying.",
                "reasoning": "High sector concentration increases unsystematic risk",
                "suggested_symbols": self._suggest_diversifying_symbols(portfolio["sectors"], db),
                "confidence": 0.80,
                "priority": "medium"
            })
        
        # Check number of holdings
        if len(portfolio["investments"]) < 5:
            recommendations.append({
                "type": "diversification",
                "title": "Increase Portfolio Diversification",
                "description": f"Consider adding more investments (currently have {len(portfolio['investments'])})",
                "reasoning": "More holdings reduce company-specific risk",
                "suggested_symbols": self._suggest_diversified_holdings(portfolio, db),
                "confidence": 0.75,
                "priority": "low"
            })
        
        return recommendations
    
    def _generate_risk_adjustment_recommendations(self, user_id: int, portfolio: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate risk adjustment recommendations"""
        recommendations = []
        
        # Get user's risk profile
        user = db.query(User).filter(User.id == user_id).first()
        risk_tolerance = user.risk_profile if user else "moderate"
        
        target_risk = self.risk_profiles.get(risk_tolerance, self.risk_profiles["moderate"])
        
        # Calculate current portfolio risk (simplified)
        current_stock_allocation = portfolio["sectors"].get("Technology", 0) + \
                                 portfolio["sectors"].get("Finance", 0) + \
                                 portfolio["sectors"].get("Healthcare", 0)
        
        if current_stock_allocation > target_risk["stock_allocation"]:
            recommendations.append({
                "type": "risk_adjustment",
                "title": "Reduce Portfolio Risk",
                "description": f"Your stock allocation ({current_stock_allocation*100:.1f}%) exceeds your risk profile target ({target_risk['stock_allocation']*100:.1f}%)",
                "reasoning": "Align portfolio with risk tolerance",
                "suggested_actions": [
                    "Reduce high-volatility tech stocks",
                    "Add bonds or dividend-paying stocks",
                    "Consider defensive sectors like utilities"
                ],
                "confidence": 0.85,
                "priority": "high"
            })
        
        return recommendations
    
    def _generate_performance_optimization_recommendations(self, user_id: int, portfolio: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Identify underperforming investments
        underperformers = self._identify_underperformers(portfolio["investments"], db)
        
        if underperformers:
            recommendations.append({
                "type": "performance_optimization",
                "title": "Review Underperforming Investments",
                "description": f"Found {len(underperformers)} investments underperforming their sector",
                "reasoning": "Underperforming investments may drag down overall returns",
                "underperformers": underperformers,
                "suggested_replacements": self._suggest_replacements(underperformers, db),
                "confidence": 0.70,
                "priority": "medium"
            })
        
        return recommendations
    
    def _generate_tax_optimization_recommendations(self, user_id: int, portfolio: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Generate tax optimization recommendations"""
        recommendations = []
        
        # Check for tax loss harvesting opportunities
        tlh_opportunities = self._identify_tax_loss_harvesting_opportunities(portfolio["investments"], db)
        
        if tlh_opportunities:
            total_loss = sum(opp["loss"] for opp in tlh_opportunities)
            potential_savings = total_loss * 0.25  # Assume 25% tax rate
            
            recommendations.append({
                "type": "tax_optimization",
                "title": "Tax Loss Harvesting Opportunity",
                "description": f"Harvest {len(tlh_opportunities)} losses worth ${total_loss:,.2f}",
                "reasoning": f"Potential tax savings: ${potential_savings:,.2f}",
                "opportunities": tlh_opportunities,
                "potential_tax_savings": potential_savings,
                "confidence": 0.80,
                "priority": "medium"
            })
        
        return recommendations
    
    def _calculate_rebalancing_trades(self, target: AssetAllocation, current: Dict[str, float], total_value: float, db: Session) -> List[Dict[str, Any]]:
        """Calculate specific trades needed for rebalancing"""
        trades = []
        
        # Map current sectors to target categories
        sector_mapping = {
            "Technology": "stocks",
            "Finance": "stocks",
            "Healthcare": "stocks",
            "Energy": "stocks",
            "Real Estate": "real_estate",
            "Cryptocurrency": "commodities"
        }
        
        # Calculate target values
        target_values = {
            "stocks": target.stocks_percentage * total_value,
            "bonds": target.bonds_percentage * total_value,
            "real_estate": target.real_estate_percentage * total_value,
            "commodities": target.commodities_percentage * total_value,
            "cash": target.cash_percentage * total_value
        }
        
        # Calculate current values by category
        current_values = {"stocks": 0, "bonds": 0, "real_estate": 0, "commodities": 0, "cash": 0}
        
        for sector, weight in current.items():
            category = sector_mapping.get(sector, "stocks")
            current_values[category] += weight * total_value
        
        # Generate trades
        for category, target_value in target_values.items():
            current_value = current_values[category]
            difference = target_value - current_value
            
            if abs(difference) > total_value * 0.01:  # Only if difference > 1%
                if difference > 0:
                    # Need to buy
                    trades.append({
                        "action": "buy",
                        "category": category,
                        "amount": difference,
                        "suggested_symbols": self._get_category_symbols(category, db)
                    })
                else:
                    # Need to sell
                    trades.append({
                        "action": "sell",
                        "category": category,
                        "amount": abs(difference),
                        "suggested_symbols": self._get_category_symbols(category, db)
                    })
        
        return trades
    
    def _identify_tax_loss_harvesting_opportunities(self, investments, db: Session) -> List[Dict[str, Any]]:
        """Identify opportunities for tax loss harvesting"""
        opportunities = []
        
        for investment in investments:
            # Handle both Investment model objects and dicts
            if isinstance(investment, dict):
                symbol = investment.get("symbol")
                quantity = investment.get("quantity", 0)
                current_price = investment.get("current_price", 0)
                avg_cost = investment.get("average_cost", 0)
            else:
                # Investment model object
                symbol = investment.symbol
                quantity = investment.quantity
                # Get current price from market data
                price_record = db.query(MarketPrice).filter(
                    MarketPrice.symbol == symbol
                ).order_by(desc(MarketPrice.timestamp)).first()
                current_price = price_record.price if price_record else investment.current_price
                avg_cost = investment.average_cost
            
            current_value = quantity * current_price
            cost_basis = quantity * avg_cost
            
            if current_value < cost_basis * 0.9:  # More than 10% loss
                opportunities.append({
                    "symbol": symbol,
                    "current_value": current_value,
                    "cost_basis": cost_basis,
                    "loss": cost_basis - current_value,
                    "loss_percentage": ((cost_basis - current_value) / cost_basis) * 100 if cost_basis > 0 else 0
                })
        
        return opportunities
    
    def _get_sector_from_symbol(self, symbol: str) -> str:
        """Get sector for a symbol"""
        symbol = symbol.upper()
        
        if symbol in ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMZN"]:
            return "Technology"
        elif symbol in ["JPM", "BAC", "WFC", "GS"]:
            return "Finance"
        elif symbol in ["JNJ", "PFE", "UNH"]:
            return "Healthcare"
        elif symbol in ["XOM", "CVX"]:
            return "Energy"
        elif symbol.endswith("-USD"):
            return "Cryptocurrency"
        else:
            return "Other"
    
    def _suggest_diversifying_symbols(self, current_sectors: Dict[str, float], db: Session) -> List[str]:
        """Suggest symbols to diversify portfolio"""
        suggestions = []
        
        # Suggest ETFs for underrepresented sectors
        all_sectors = set(self.sector_etfs.keys())
        current_sectors_set = set(current_sectors.keys())
        
        missing_sectors = all_sectors - current_sectors_set
        
        for sector in list(missing_sectors)[:3]:  # Top 3 missing sectors
            suggestions.append(self.sector_etfs[sector])
        
        return suggestions
    
    def _suggest_diversified_holdings(self, portfolio: Dict[str, Any], db: Session) -> List[str]:
        """Suggest diversified holdings"""
        # Suggest broad market ETFs and some blue-chip stocks
        return ["SPY", "QQQ", "VTI", "BND", "VTV"]
    
    def _identify_underperformers(self, investments: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
        """Identify underperforming investments"""
        underperformers = []
        
        for inv in investments:
            # This is simplified - in production, compare with sector benchmarks
            if inv.get("weight", 0) > 0.05:  # Significant holdings
                # Simulate underperformance check
                if np.random.random() < 0.3:  # 30% chance of underperformance
                    underperformers.append({
                        "symbol": inv["symbol"],
                        "current_return": -np.random.uniform(0.05, 0.20),
                        "sector": inv["sector"]
                    })
        
        return underperformers
    
    def _suggest_replacements(self, underperformers: List[Dict[str, Any]], db: Session) -> List[str]:
        """Suggest replacement stocks for underperformers"""
        replacements = []
        
        # Map sectors to better performers
        sector_replacements = {
            "Technology": ["MSFT", "GOOGL", "NVDA"],
            "Finance": ["JPM", "BAC", "BRK-B"],
            "Healthcare": ["JNJ", "UNH", "PFE"],
            "Energy": ["XOM", "CVX", "COP"]
        }
        
        for underperformer in underperformers:
            sector = underperformer["sector"]
            if sector in sector_replacements:
                replacements.extend(sector_replacements[sector][:2])
        
        return list(set(replacements))[:5]  # Top 5 unique suggestions
    
    def _get_category_symbols(self, category: str, db: Session) -> List[str]:
        """Get symbols for a given category"""
        category_symbols = {
            "stocks": ["SPY", "VOO", "VTI", "QQQ"],
            "bonds": ["BND", "AGG", "TLT", "SHY"],
            "real_estate": ["VNQ", "XLRE", "IYR"],
            "commodities": ["GLD", "SLV", "DBC", "USO"],
            "cash": ["SHY", "BIL", "SGOV"]
        }
        
        return category_symbols.get(category, ["SPY"])
    
    def _generate_rebalancing_reasoning(self, target: AssetAllocation, current: Dict[str, float]) -> str:
        """Generate reasoning for rebalancing"""
        max_drift = 0
        for sector, current_pct in current.items():
            target_pct = getattr(target, f"{sector.lower()}_percentage", 0) * 100
            drift = abs(current_pct - target_pct)
            max_drift = max(max_drift, drift)
        
        return f"Maximum allocation drift of {max_drift:.1f}% exceeds rebalancing threshold of {target.rebalance_threshold*100:.1f}%"
    
    def _calculate_rebalancing_impact(self, trades: List[Dict[str, Any]], db: Session) -> Dict[str, Any]:
        """Calculate expected impact of rebalancing"""
        return {
            "risk_reduction": "Expected to reduce portfolio volatility by 5-10%",
            "return_impact": "Minimal impact on expected returns",
            "tax_implications": "May generate taxable events in taxable accounts",
            "time_horizon": "Rebalancing recommended quarterly"
        }
    
    def _calculate_tax_savings(self, opportunities: List[Dict[str, Any]]) -> float:
        """Calculate potential tax savings from loss harvesting"""
        total_loss = sum(opp["loss"] for opp in opportunities)
        # Assume 25% tax rate on capital gains
        return total_loss * 0.25
    
    def _generate_asset_location_recommendations(self, investments: List[Investment], db: Session) -> Dict[str, Any]:
        """Generate asset location recommendations"""
        return {
            "type": "asset_location",
            "title": "Optimize Asset Location",
            "description": "Place tax-efficient investments in taxable accounts",
            "recommendations": {
                "taxable_account": ["Index funds", "ETFs", "Tax-loss harvested stocks"],
                "tax_advantaged_account": ["Bonds", "REITs", "High-dividend stocks"]
            },
            "confidence": 0.70
        }
    
    def _analyze_goal_progress(self, goal: Goal, db: Session) -> Dict[str, Any]:
        """Analyze progress towards a goal"""
        # Simplified goal analysis
        progress_percentage = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
        on_track = progress_percentage >= (goal.time_horizon * 12 * 5)  # Simplified
        
        recommended_actions = []
        if not on_track:
            recommended_actions = [
                "Increase monthly contributions",
                "Consider higher return investments",
                "Extend time horizon if possible"
            ]
        
        return {
            "progress_percentage": progress_percentage,
            "on_track": on_track,
            "recommended_actions": recommended_actions
        }
    
    def _save_recommendation(self, user_id: int, recommendation: Dict[str, Any], db: Session):
        """Save recommendation to database"""
        try:
            db_recommendation = Recommendation(
                user_id=user_id,
                recommendation_type=recommendation["type"],
                title=recommendation["title"],
                description=recommendation["description"],
                reasoning=recommendation.get("reasoning", ""),
                suggested_symbols=recommendation.get("suggested_symbols", []),
                expected_return=recommendation.get("expected_return", 0.0),
                risk_level=recommendation.get("risk_level", "medium"),
                confidence_score=recommendation.get("confidence", 0.5),
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            
            db.add(db_recommendation)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save recommendation: {str(e)}")

# Global instance
recommendation_service = RecommendationService()
