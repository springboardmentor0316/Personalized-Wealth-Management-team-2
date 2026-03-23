import math
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimulationService:
    
    @staticmethod
    def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        years: int,
        compound_frequency: int = 12
    ) -> float:
        """
        Calculate compound interest
        principal: initial amount
        annual_rate: annual interest rate (as decimal, e.g., 0.08 for 8%)
        years: investment period in years
        compound_frequency: number of times interest is compounded per year
        """
        if principal <= 0 or annual_rate < 0 or years <= 0:
            return 0
        
        amount = principal * (1 + annual_rate / compound_frequency) ** (compound_frequency * years)
        return amount
    
    @staticmethod
    def calculate_sip_future_value(
        monthly_investment: float,
        annual_rate: float,
        years: int
    ) -> float:
        """
        Calculate Systematic Investment Plan (SIP) future value
        monthly_investment: fixed monthly investment amount
        annual_rate: expected annual return rate (as decimal)
        years: investment period in years
        """
        if monthly_investment <= 0 or annual_rate < 0 or years <= 0:
            return 0
        
        monthly_rate = annual_rate / 12
        total_months = years * 12
        
        if monthly_rate == 0:
            return monthly_investment * total_months
        
        # SIP formula: FV = P × [(1 + r)^n - 1] / r × (1 + r)
        future_value = monthly_investment * ((1 + monthly_rate) ** total_months - 1) / monthly_rate * (1 + monthly_rate)
        
        return future_value
    
    @staticmethod
    def calculate_combined_investment(
        initial_amount: float,
        monthly_investment: float,
        annual_rate: float,
        years: int
    ) -> Dict:
        """
        Calculate combined investment (lumpsum + SIP)
        """
        try:
            # Calculate lumpsum future value
            lumpsum_fv = SimulationService.calculate_compound_interest(
                initial_amount, annual_rate, years
            )
            
            # Calculate SIP future value
            sip_fv = SimulationService.calculate_sip_future_value(
                monthly_investment, annual_rate, years
            )
            
            # Calculate total investment
            total_investment = initial_amount + (monthly_investment * years * 12)
            
            # Calculate total returns
            total_fv = lumpsum_fv + sip_fv
            total_returns = total_fv - total_investment
            return_percentage = (total_returns / total_investment * 100) if total_investment > 0 else 0
            
            # Generate year-by-year breakdown
            yearly_breakdown = []
            for year in range(1, years + 1):
                year_lumpsum = SimulationService.calculate_compound_interest(
                    initial_amount, annual_rate, year
                )
                year_sip = SimulationService.calculate_sip_future_value(
                    monthly_investment, annual_rate, year
                )
                year_total_investment = initial_amount + (monthly_investment * year * 12)
                year_total_fv = year_lumpsum + year_sip
                year_returns = year_total_fv - year_total_investment
                
                yearly_breakdown.append({
                    "year": year,
                    "lumpsum_value": round(year_lumpsum, 2),
                    "sip_value": round(year_sip, 2),
                    "total_value": round(year_total_fv, 2),
                    "total_investment": round(year_total_investment, 2),
                    "returns": round(year_returns, 2),
                    "return_percentage": round((year_returns / year_total_investment * 100) if year_total_investment > 0 else 0, 2)
                })
            
            return {
                "initial_amount": initial_amount,
                "monthly_investment": monthly_investment,
                "annual_rate": annual_rate,
                "years": years,
                "lumpsum_future_value": round(lumpsum_fv, 2),
                "sip_future_value": round(sip_fv, 2),
                "total_future_value": round(total_fv, 2),
                "total_investment": round(total_investment, 2),
                "total_returns": round(total_returns, 2),
                "return_percentage": round(return_percentage, 2),
                "yearly_breakdown": yearly_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error in combined investment calculation: {e}")
            raise ValueError(f"Calculation error: {str(e)}")
    
    @staticmethod
    def calculate_what_if_scenarios(
        initial_amount: float,
        monthly_investment: float,
        scenarios: List[Dict]
    ) -> Dict:
        """
        Calculate multiple what-if scenarios
        scenarios: list of dicts with 'name', 'annual_rate', 'years'
        """
        try:
            results = []
            
            for scenario in scenarios:
                if not all(key in scenario for key in ['name', 'annual_rate', 'years']):
                    continue
                
                result = SimulationService.calculate_combined_investment(
                    initial_amount,
                    monthly_investment,
                    scenario['annual_rate'],
                    scenario['years']
                )
                result['scenario_name'] = scenario['name']
                results.append(result)
            
            # Sort by total future value
            results.sort(key=lambda x: x['total_future_value'], reverse=True)
            
            return {
                "initial_amount": initial_amount,
                "monthly_investment": monthly_investment,
                "scenarios": results,
                "best_scenario": results[0] if results else None,
                "worst_scenario": results[-1] if results else None
            }
            
        except Exception as e:
            logger.error(f"Error in what-if scenarios calculation: {e}")
            raise ValueError(f"Scenario calculation error: {str(e)}")
    
    @staticmethod
    def calculate_goal_projection(
        target_amount: float,
        current_amount: float,
        monthly_contribution: float,
        annual_rate: float
    ) -> Dict:
        """
        Calculate time needed to reach a financial goal
        """
        try:
            if target_amount <= current_amount:
                return {
                    "target_amount": target_amount,
                    "current_amount": current_amount,
                    "monthly_contribution": monthly_contribution,
                    "annual_rate": annual_rate,
                    "years_needed": 0,
                    "months_needed": 0,
                    "achievable": True,
                    "final_amount": current_amount
                }
            
            # Use iterative approach to find the time needed
            monthly_rate = annual_rate / 12
            years_needed = 0
            max_years = 50  # Maximum search limit
            
            for year in range(1, max_years + 1):
                future_value = SimulationService.calculate_combined_investment(
                    current_amount, monthly_contribution, annual_rate, year
                )['total_future_value']
                
                if future_value >= target_amount:
                    years_needed = year
                    break
            
            if years_needed == 0:
                return {
                    "target_amount": target_amount,
                    "current_amount": current_amount,
                    "monthly_contribution": monthly_contribution,
                    "annual_rate": annual_rate,
                    "years_needed": None,
                    "months_needed": None,
                    "achievable": False,
                    "final_amount": SimulationService.calculate_combined_investment(
                        current_amount, monthly_contribution, annual_rate, max_years
                    )['total_future_value']
                }
            
            # Calculate final amount
            final_amount = SimulationService.calculate_combined_investment(
                current_amount, monthly_contribution, annual_rate, years_needed
            )['total_future_value']
            
            return {
                "target_amount": target_amount,
                "current_amount": current_amount,
                "monthly_contribution": monthly_contribution,
                "annual_rate": annual_rate,
                "years_needed": years_needed,
                "months_needed": years_needed * 12,
                "achievable": True,
                "final_amount": final_amount
            }
            
        except Exception as e:
            logger.error(f"Error in goal projection calculation: {e}")
            raise ValueError(f"Goal projection error: {str(e)}")

# Global instance
simulation_service = SimulationService()
