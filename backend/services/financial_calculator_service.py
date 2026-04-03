"""
Financial Calculators Service
Provides calculations for SIP, Retirement, and Loan Payoff
"""

import math
from typing import Dict, Any
from datetime import datetime, timedelta


class FinancialCalculatorService:
    """Service for financial calculations"""
    
    def calculate_sip(self, monthly_investment: float, expected_return: float, 
                     time_period_years: int) -> Dict[str, Any]:
        """
        Calculate Systematic Investment Plan (SIP) returns
        
        Args:
            monthly_investment: Monthly investment amount
            expected_return: Expected annual return rate (percentage)
            time_period_years: Investment period in years
            
        Returns:
            Dictionary with SIP calculation results
        """
        try:
            # Convert annual return to monthly rate
            monthly_rate = expected_return / 12 / 100
            
            # Total number of months
            total_months = time_period_years * 12
            
            # Calculate future value using compound interest formula
            # FV = P × ({(1 + r)^n - 1} / r) × (1 + r)
            future_value = monthly_investment * \
                          ((math.pow(1 + monthly_rate, total_months) - 1) / monthly_rate) * \
                          (1 + monthly_rate)
            
            # Total investment
            total_investment = monthly_investment * total_months
            
            # Wealth gained
            wealth_gained = future_value - total_investment
            
            return {
                "monthly_investment": monthly_investment,
                "expected_return": expected_return,
                "time_period_years": time_period_years,
                "total_investment": round(total_investment, 2),
                "wealth_gained": round(wealth_gained, 2),
                "future_value": round(future_value, 2),
                "monthly_rate": round(monthly_rate * 100, 2),
                "total_months": total_months,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"SIP calculation failed: {str(e)}")
    
    def calculate_retirement(self, current_age: int, retirement_age: int, 
                            current_savings: float, monthly_contribution: float,
                            expected_return: float, inflation_rate: float) -> Dict[str, Any]:
        """
        Calculate retirement corpus and monthly income
        
        Args:
            current_age: Current age
            retirement_age: Target retirement age
            current_savings: Current savings amount
            monthly_contribution: Monthly contribution to retirement fund
            expected_return: Expected annual return rate (percentage)
            inflation_rate: Expected annual inflation rate (percentage)
            
        Returns:
            Dictionary with retirement calculation results
        """
        try:
            # Years until retirement
            years_to_retirement = retirement_age - current_age
            
            if years_to_retirement <= 0:
                raise ValueError("Retirement age must be greater than current age")
            
            # Convert annual rates to monthly
            monthly_return = expected_return / 12 / 100
            monthly_inflation = inflation_rate / 12 / 100
            
            # Total months
            total_months = years_to_retirement * 12
            
            # Future value of current savings
            # FV = PV × (1 + r)^n
            future_current_savings = current_savings * math.pow(1 + monthly_return, total_months)
            
            # Future value of monthly contributions
            # FV = P × ({(1 + r)^n - 1} / r) × (1 + r)
            future_contributions = monthly_contribution * \
                                 ((math.pow(1 + monthly_return, total_months) - 1) / monthly_return) * \
                                 (1 + monthly_return)
            
            # Total retirement corpus
            retirement_corpus = future_current_savings + future_contributions
            
            # Calculate monthly income in today's terms (accounting for inflation)
            # Assuming 4% withdrawal rate in retirement
            annual_withdrawal_rate = 0.04
            annual_income = retirement_corpus * annual_withdrawal_rate
            monthly_income = annual_income / 12
            
            # Adjust for inflation to get purchasing power
            inflation_factor = math.pow(1 + monthly_inflation, total_months)
            monthly_income_today = monthly_income / inflation_factor
            
            # Total contributions
            total_contributions = monthly_contribution * total_months
            
            return {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "years_to_retirement": years_to_retirement,
                "current_savings": round(current_savings, 2),
                "monthly_contribution": round(monthly_contribution, 2),
                "expected_return": expected_return,
                "inflation_rate": inflation_rate,
                "future_current_savings": round(future_current_savings, 2),
                "future_contributions": round(future_contributions, 2),
                "retirement_corpus": round(retirement_corpus, 2),
                "monthly_income": round(monthly_income, 2),
                "monthly_income_today": round(monthly_income_today, 2),
                "total_contributions": round(total_contributions, 2),
                "wealth_gained": round(retirement_corpus - current_savings - total_contributions, 2),
                "inflation_factor": round(inflation_factor, 2),
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Retirement calculation failed: {str(e)}")
    
    def calculate_loan_payoff(self, principal: float, interest_rate: float, 
                             loan_term_years: int, extra_payment: float = 0) -> Dict[str, Any]:
        """
        Calculate loan payoff schedule and total interest
        
        Args:
            principal: Loan principal amount
            interest_rate: Annual interest rate (percentage)
            loan_term_years: Loan term in years
            extra_payment: Additional monthly payment (optional)
            
        Returns:
            Dictionary with loan payoff calculation results
        """
        try:
            # Convert annual rate to monthly
            monthly_rate = interest_rate / 12 / 100
            
            # Total months
            total_months = loan_term_years * 12
            
            # Calculate monthly payment using amortization formula
            # M = P × [r(1+r)^n] / [(1+r)^n - 1]
            if monthly_rate == 0:
                monthly_payment = principal / total_months
            else:
                monthly_payment = principal * \
                                (monthly_rate * math.pow(1 + monthly_rate, total_months)) / \
                                (math.pow(1 + monthly_rate, total_months) - 1)
            
            # Calculate with extra payment
            effective_monthly_payment = monthly_payment + extra_payment
            
            # Calculate payoff with extra payment
            if extra_payment > 0:
                # Use iterative approach to calculate new payoff time
                balance = principal
                months_to_payoff = 0
                total_interest_extra = 0
                
                while balance > 0 and months_to_payoff < total_months * 2:
                    interest_payment = balance * monthly_rate
                    principal_payment = effective_monthly_payment - interest_payment
                    
                    if principal_payment <= 0:
                        break
                    
                    balance -= principal_payment
                    total_interest_extra += interest_payment
                    months_to_payoff += 1
                
                months_saved = total_months - months_to_payoff
                years_saved = months_saved / 12
                total_amount_extra = principal + total_interest_extra
            else:
                months_to_payoff = total_months
                months_saved = 0
                years_saved = 0
                total_amount_extra = None
                total_interest_extra = None
            
            # Calculate total interest (without extra payment)
            total_amount = monthly_payment * total_months
            total_interest = total_amount - principal
            
            return {
                "principal": round(principal, 2),
                "interest_rate": interest_rate,
                "loan_term_years": loan_term_years,
                "extra_payment": round(extra_payment, 2),
                "monthly_payment": round(monthly_payment, 2),
                "effective_monthly_payment": round(effective_monthly_payment, 2),
                "total_months": total_months,
                "total_amount": round(total_amount, 2),
                "total_interest": round(total_interest, 2),
                "months_to_payoff": months_to_payoff,
                "months_saved": months_saved,
                "years_saved": round(years_saved, 1),
                "total_amount_extra": round(total_amount_extra, 2) if total_amount_extra else None,
                "total_interest_extra": round(total_interest_extra, 2) if total_interest_extra else None,
                "interest_saved": round(total_interest - total_interest_extra, 2) if total_interest_extra else None,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Loan payoff calculation failed: {str(e)}")
    
    def calculate_compound_interest(self, principal: float, annual_rate: float,
                                   time_years: int, compounding_frequency: int = 1) -> Dict[str, Any]:
        """
        Calculate compound interest
        
        Args:
            principal: Initial investment amount
            annual_rate: Annual interest rate (percentage)
            time_years: Investment period in years
            compounding_frequency: Times per year interest is compounded (1=annual, 12=monthly)
            
        Returns:
            Dictionary with compound interest calculation results
        """
        try:
            # Convert rate to decimal
            rate = annual_rate / 100
            
            # Calculate future value
            # A = P(1 + r/n)^(nt)
            future_value = principal * \
                          math.pow(1 + rate / compounding_frequency, 
                                   compounding_frequency * time_years)
            
            # Calculate compound interest
            compound_interest = future_value - principal
            
            return {
                "principal": round(principal, 2),
                "annual_rate": annual_rate,
                "time_years": time_years,
                "compounding_frequency": compounding_frequency,
                "future_value": round(future_value, 2),
                "compound_interest": round(compound_interest, 2),
                "total_periods": compounding_frequency * time_years,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Compound interest calculation failed: {str(e)}")
    
    def calculate_goal_progress(self, current_amount: float, target_amount: float,
                               monthly_contribution: float, expected_return: float,
                               target_date: str) -> Dict[str, Any]:
        """
        Calculate goal progress and time to reach target
        
        Args:
            current_amount: Current amount saved
            target_amount: Target amount
            monthly_contribution: Monthly contribution
            expected_return: Expected annual return (percentage)
            target_date: Target date (YYYY-MM-DD)
            
        Returns:
            Dictionary with goal progress calculation results
        """
        try:
            # Parse target date
            target_datetime = datetime.strptime(target_date, "%Y-%m-%d")
            current_datetime = datetime.utcnow()
            
            # Calculate months remaining
            months_remaining = (target_datetime.year - current_datetime.year) * 12 + \
                              (target_datetime.month - current_datetime.month)
            
            if months_remaining <= 0:
                raise ValueError("Target date must be in the future")
            
            # Calculate current progress
            progress_percentage = (current_amount / target_amount) * 100
            
            # Calculate projected amount at target date
            monthly_rate = expected_return / 12 / 100
            
            # Future value of current savings
            future_current = current_amount * math.pow(1 + monthly_rate, months_remaining)
            
            # Future value of monthly contributions
            future_contributions = monthly_contribution * \
                                 ((math.pow(1 + monthly_rate, months_remaining) - 1) / monthly_rate) * \
                                 (1 + monthly_rate)
            
            projected_amount = future_current + future_contributions
            
            # Check if goal will be reached
            goal_achieved = projected_amount >= target_amount
            
            # Calculate years to reach goal if not achieved
            if not goal_achieved:
                # Use binary search to find time to reach target
                low = months_remaining
                high = months_remaining * 10
                months_to_goal = None
                
                while low <= high:
                    mid = (low + high) // 2
                    future_current_mid = current_amount * math.pow(1 + monthly_rate, mid)
                    future_contributions_mid = monthly_contribution * \
                                             ((math.pow(1 + monthly_rate, mid) - 1) / monthly_rate) * \
                                             (1 + monthly_rate)
                    projected_mid = future_current_mid + future_contributions_mid
                    
                    if projected_mid >= target_amount:
                        months_to_goal = mid
                        high = mid - 1
                    else:
                        low = mid + 1
                
                years_to_goal = months_to_goal / 12 if months_to_goal else None
            else:
                months_to_goal = None
                years_to_goal = None
            
            return {
                "current_amount": round(current_amount, 2),
                "target_amount": round(target_amount, 2),
                "monthly_contribution": round(monthly_contribution, 2),
                "expected_return": expected_return,
                "target_date": target_date,
                "months_remaining": months_remaining,
                "progress_percentage": round(progress_percentage, 2),
                "projected_amount": round(projected_amount, 2),
                "goal_achieved": goal_achieved,
                "months_to_goal": months_to_goal,
                "years_to_goal": round(years_to_goal, 1) if years_to_goal else None,
                "shortfall": round(target_amount - projected_amount, 2) if not goal_achieved else 0,
                "surplus": round(projected_amount - target_amount, 2) if goal_achieved else 0,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Goal progress calculation failed: {str(e)}")


# Global instance
financial_calculator_service = FinancialCalculatorService()
