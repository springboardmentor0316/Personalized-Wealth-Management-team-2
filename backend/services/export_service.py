"""
Export Service for Reports
Provides PDF and CSV export functionality
"""

import csv
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Goal, Investment, Transaction
from models_pkg.analytics import PortfolioSnapshot, PerformanceMetrics, Recommendation


class ExportService:
    """Service for exporting reports in PDF and CSV formats"""
    
    def export_portfolio_to_csv(self, user_id: int, db: Session) -> str:
        """
        Export portfolio data to CSV format
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CSV formatted string
        """
        try:
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Symbol", "Name", "Type", "Quantity", 
                "Average Cost", "Current Price", "Current Value",
                "Cost Basis", "Gain/Loss", "Gain/Loss %", "Date"
            ])
            
            # Write investment data
            total_value = 0
            total_cost = 0
            
            for inv in investments:
                current_value = inv.quantity * inv.current_price
                cost_basis = inv.quantity * inv.average_cost
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                writer.writerow([
                    inv.symbol,
                    inv.name,
                    inv.type.value if hasattr(inv.type, 'value') else str(inv.type),
                    inv.quantity,
                    inv.average_cost,
                    inv.current_price,
                    current_value,
                    cost_basis,
                    gain_loss,
                    f"{gain_loss_percent:.2f}%",
                    inv.created_at.strftime("%Y-%m-%d")
                ])
                
                total_value += current_value
                total_cost += cost_basis
            
            # Write summary
            writer.writerow([])
            writer.writerow(["Portfolio Summary"])
            writer.writerow(["Total Value", total_value])
            writer.writerow(["Total Cost", total_cost])
            writer.writerow(["Total Gain/Loss", total_value - total_cost])
            writer.writerow(["Total Gain/Loss %", f"{((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0:.2f}%"])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export portfolio to CSV: {str(e)}")
    
    def export_goals_to_csv(self, user_id: int, db: Session) -> str:
        """
        Export goals data to CSV format
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CSV formatted string
        """
        try:
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Goal", "Description", "Target Amount", "Current Amount",
                "Progress %", "Target Date", "Monthly Contribution", "Status"
            ])
            
            # Write goal data
            for goal in goals:
                progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                
                writer.writerow([
                    goal.title,
                    goal.description or "",
                    goal.target_amount,
                    goal.current_amount,
                    f"{progress:.2f}%",
                    goal.target_date.strftime("%Y-%m-%d"),
                    goal.monthly_contribution,
                    goal.status
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export goals to CSV: {str(e)}")
    
    def export_transactions_to_csv(self, user_id: int, db: Session, 
                                    start_date: Optional[str] = None,
                                    end_date: Optional[str] = None) -> str:
        """
        Export transactions data to CSV format
        
        Args:
            user_id: User ID
            db: Database session
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            
        Returns:
            CSV formatted string
        """
        try:
            query = db.query(Transaction).filter(Transaction.user_id == user_id)
            
            if start_date:
                query = query.filter(Transaction.date >= datetime.strptime(start_date, "%Y-%m-%d"))
            if end_date:
                query = query.filter(Transaction.date <= datetime.strptime(end_date, "%Y-%m-%d"))
            
            transactions = query.order_by(Transaction.date.desc()).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Date", "Symbol", "Type", "Quantity", "Price", "Amount", "Status"
            ])
            
            # Write transaction data
            for txn in transactions:
                writer.writerow([
                    txn.date.strftime("%Y-%m-%d"),
                    txn.symbol,
                    txn.type.value if hasattr(txn.type, 'value') else str(txn.type),
                    txn.quantity,
                    txn.price,
                    txn.amount,
                    "Completed"
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export transactions to CSV: {str(e)}")
    
    def export_performance_metrics_to_csv(self, user_id: int, db: Session) -> str:
        """
        Export performance metrics to CSV format
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CSV formatted string
        """
        try:
            metrics = db.query(PerformanceMetrics).filter(
                PerformanceMetrics.user_id == user_id
            ).order_by(PerformanceMetrics.created_at.desc()).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Period", "Start Date", "End Date", "Total Return %",
                "Annualized Return %", "Volatility", "Sharpe Ratio",
                "Max Drawdown %", "Win Rate %", "Benchmark Return %",
                "Excess Return %", "Date"
            ])
            
            # Write metrics data
            for metric in metrics:
                writer.writerow([
                    metric.period,
                    metric.start_date.strftime("%Y-%m-%d"),
                    metric.end_date.strftime("%Y-%m-%d"),
                    f"{metric.total_return * 100:.2f}%",
                    f"{metric.annualized_return * 100:.2f}%",
                    f"{metric.volatility:.2f}",
                    f"{metric.sharpe_ratio:.2f}",
                    f"{metric.max_drawdown * 100:.2f}%",
                    f"{metric.win_rate * 100:.2f}%",
                    f"{metric.benchmark_return * 100:.2f}%",
                    f"{metric.excess_return * 100:.2f}%",
                    metric.created_at.strftime("%Y-%m-%d")
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export performance metrics to CSV: {str(e)}")
    
    def export_recommendations_to_csv(self, user_id: int, db: Session) -> str:
        """
        Export recommendations to CSV format
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CSV formatted string
        """
        try:
            recommendations = db.query(Recommendation).filter(
                Recommendation.user_id == user_id
            ).order_by(Recommendation.created_at.desc()).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Type", "Title", "Description", "Reasoning",
                "Confidence %", "Priority", "Status", "Created Date"
            ])
            
            # Write recommendation data
            for rec in recommendations:
                writer.writerow([
                    rec.recommendation_type,
                    rec.title,
                    rec.description,
                    rec.reasoning or "",
                    f"{rec.confidence_score * 100:.2f}%" if rec.confidence_score else "N/A",
                    rec.priority or "N/A",
                    rec.status,
                    rec.created_at.strftime("%Y-%m-%d")
                ])
            
            return output.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to export recommendations to CSV: {str(e)}")
    
    def generate_portfolio_summary_html(self, user_id: int, db: Session) -> str:
        """
        Generate HTML summary for PDF export
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            HTML formatted string
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            investments = db.query(Investment).filter(Investment.user_id == user_id).all()
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            
            total_value = sum(inv.quantity * inv.current_price for inv in investments)
            total_cost = sum(inv.quantity * inv.average_cost for inv in investments)
            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Portfolio Report - {user.full_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .section {{ margin-bottom: 30px; }}
                    .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background: #4CAF50; color: white; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Wealth Management Portfolio Report</h1>
                    <h2>{user.full_name}</h2>
                    <p>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
                </div>
                
                <div class="section summary">
                    <h3>Portfolio Summary</h3>
                    <p><strong>Total Value:</strong> ${total_value:,.2f}</p>
                    <p><strong>Total Cost:</strong> ${total_cost:,.2f}</p>
                    <p><strong>Total Gain/Loss:</strong> <span class="{'positive' if total_gain_loss >= 0 else 'negative'}">${total_gain_loss:,.2f} ({total_gain_loss_percent:.2f}%)</span></p>
                </div>
                
                <div class="section">
                    <h3>Investments ({len(investments)})</h3>
                    <table>
                        <tr>
                            <th>Symbol</th>
                            <th>Name</th>
                            <th>Quantity</th>
                            <th>Average Cost</th>
                            <th>Current Price</th>
                            <th>Current Value</th>
                            <th>Gain/Loss</th>
                            <th>Gain/Loss %</th>
                        </tr>
            """
            
            for inv in investments:
                current_value = inv.quantity * inv.current_price
                cost_basis = inv.quantity * inv.average_cost
                gain_loss = current_value - cost_basis
                gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
                
                html += f"""
                        <tr>
                            <td>{inv.symbol}</td>
                            <td>{inv.name}</td>
                            <td>{inv.quantity}</td>
                            <td>${inv.average_cost:.2f}</td>
                            <td>${inv.current_price:.2f}</td>
                            <td>${current_value:.2f}</td>
                            <td class="{'positive' if gain_loss >= 0 else 'negative'}">${gain_loss:.2f}</td>
                            <td class="{'positive' if gain_loss >= 0 else 'negative'}">{gain_loss_percent:.2f}%</td>
                        </tr>
                """
            
            html += """
                    </table>
                </div>
                
                <div class="section">
                    <h3>Goals</h3>
                    <table>
                        <tr>
                            <th>Goal</th>
                            <th>Target Amount</th>
                            <th>Current Amount</th>
                            <th>Progress</th>
                            <th>Status</th>
                        </tr>
            """
            
            for goal in goals:
                progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                html += f"""
                        <tr>
                            <td>{goal.title}</td>
                            <td>${goal.target_amount:,.2f}</td>
                            <td>${goal.current_amount:,.2f}</td>
                            <td>{progress:.2f}%</td>
                            <td>{goal.status}</td>
                        </tr>
                """
            
            html += """
                    </table>
                </div>
                
                <div class="section">
                    <p><em>This report was generated automatically by the Wealth Management System.</em></p>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            raise Exception(f"Failed to generate portfolio summary HTML: {str(e)}")


# Global instance
export_service = ExportService()
