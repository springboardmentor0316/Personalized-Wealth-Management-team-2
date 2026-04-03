"""
API Routes for Financial Calculators
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from database import get_db
from services.financial_calculator_service import financial_calculator_service
import schemas
import models
from auth import get_current_user

router = APIRouter(prefix="/api/calculators", tags=["calculators"])


@router.post("/sip")
def calculate_sip(
    request: schemas.SIPCalculatorRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate Systematic Investment Plan (SIP) returns
    """
    try:
        if request.monthly_investment <= 0:
            raise HTTPException(status_code=400, detail="Monthly investment must be positive")
        if request.expected_return < 0:
            raise HTTPException(status_code=400, detail="Expected return cannot be negative")
        if request.time_period_years <= 0:
            raise HTTPException(status_code=400, detail="Time period must be positive")
        
        result = financial_calculator_service.calculate_sip(
            monthly_investment=request.monthly_investment,
            expected_return=request.expected_return,
            time_period_years=request.time_period_years
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retirement")
def calculate_retirement(
    request: schemas.RetirementCalculatorRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate retirement corpus and monthly income
    """
    try:
        if request.current_age <= 0:
            raise HTTPException(status_code=400, detail="Current age must be positive")
        if request.retirement_age <= request.current_age:
            raise HTTPException(status_code=400, detail="Retirement age must be greater than current age")
        if request.current_savings < 0:
            raise HTTPException(status_code=400, detail="Current savings cannot be negative")
        if request.monthly_contribution < 0:
            raise HTTPException(status_code=400, detail="Monthly contribution cannot be negative")
        if request.expected_return < 0:
            raise HTTPException(status_code=400, detail="Expected return cannot be negative")
        if request.inflation_rate < 0:
            raise HTTPException(status_code=400, detail="Inflation rate cannot be negative")
        
        result = financial_calculator_service.calculate_retirement(
            current_age=request.current_age,
            retirement_age=request.retirement_age,
            current_savings=request.current_savings,
            monthly_contribution=request.monthly_contribution,
            expected_return=request.expected_return,
            inflation_rate=request.inflation_rate
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/loan-payoff")
def calculate_loan_payoff(
    request: schemas.LoanPayoffRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate loan payoff schedule and total interest
    """
    try:
        if request.principal <= 0:
            raise HTTPException(status_code=400, detail="Principal must be positive")
        if request.interest_rate < 0:
            raise HTTPException(status_code=400, detail="Interest rate cannot be negative")
        if request.loan_term_years <= 0:
            raise HTTPException(status_code=400, detail="Loan term must be positive")
        if request.extra_payment < 0:
            raise HTTPException(status_code=400, detail="Extra payment cannot be negative")
        
        result = financial_calculator_service.calculate_loan_payoff(
            principal=request.principal,
            interest_rate=request.interest_rate,
            loan_term_years=request.loan_term_years,
            extra_payment=request.extra_payment
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compound-interest")
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    time_years: int,
    compounding_frequency: int = 1,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate compound interest
    
    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate (percentage)
        time_years: Investment period in years
        compounding_frequency: Times per year interest is compounded (1=annual, 12=monthly)
    """
    try:
        if principal <= 0:
            raise HTTPException(status_code=400, detail="Principal must be positive")
        if annual_rate < 0:
            raise HTTPException(status_code=400, detail="Annual rate cannot be negative")
        if time_years <= 0:
            raise HTTPException(status_code=400, detail="Time period must be positive")
        if compounding_frequency not in [1, 2, 4, 12, 52, 365]:
            raise HTTPException(status_code=400, detail="Invalid compounding frequency")
        
        result = financial_calculator_service.calculate_compound_interest(
            principal=principal,
            annual_rate=annual_rate,
            time_years=time_years,
            compounding_frequency=compounding_frequency
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goal-progress")
def calculate_goal_progress(
    current_amount: float,
    target_amount: float,
    monthly_contribution: float,
    expected_return: float,
    target_date: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Calculate goal progress and time to reach target
    
    Args:
        current_amount: Current amount saved
        target_amount: Target amount
        monthly_contribution: Monthly contribution
        expected_return: Expected annual return (percentage)
        target_date: Target date (YYYY-MM-DD)
    """
    try:
        if current_amount < 0:
            raise HTTPException(status_code=400, detail="Current amount cannot be negative")
        if target_amount <= 0:
            raise HTTPException(status_code=400, detail="Target amount must be positive")
        if monthly_contribution < 0:
            raise HTTPException(status_code=400, detail="Monthly contribution cannot be negative")
        if expected_return < 0:
            raise HTTPException(status_code=400, detail="Expected return cannot be negative")
        
        result = financial_calculator_service.calculate_goal_progress(
            current_amount=current_amount,
            target_amount=target_amount,
            monthly_contribution=monthly_contribution,
            expected_return=expected_return,
            target_date=target_date
        )
        
        return {"success": True, "data": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
