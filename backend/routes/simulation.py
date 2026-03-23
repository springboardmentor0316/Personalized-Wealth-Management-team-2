from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from services.simulation_service import simulation_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simulate", tags=["simulation"])

class SimulationRequest(BaseModel):
    initial_amount: float = Field(..., gt=0, description="Initial lumpsum investment amount")
    monthly_investment: float = Field(..., gt=0, description="Monthly SIP investment amount")
    annual_rate: float = Field(..., gt=0, description="Expected annual return rate (as decimal, e.g., 0.08 for 8%)")
    years: int = Field(..., gt=0, le=50, description="Investment period in years")

class WhatIfRequest(BaseModel):
    initial_amount: float = Field(..., gt=0, description="Initial lumpsum investment amount")
    monthly_investment: float = Field(..., gt=0, description="Monthly SIP investment amount")
    scenarios: List[Dict] = Field(..., description="List of scenarios with name, annual_rate, and years")

class GoalProjectionRequest(BaseModel):
    target_amount: float = Field(..., gt=0, description="Target goal amount")
    current_amount: float = Field(default=0, ge=0, description="Current saved amount")
    monthly_contribution: float = Field(..., gt=0, description="Monthly contribution amount")
    annual_rate: float = Field(..., gt=0, description="Expected annual return rate (as decimal)")

@router.post("/")
async def simulate_investment(request: SimulationRequest):
    """
    Simulate investment growth with lumpsum and SIP components
    """
    try:
        result = simulation_service.calculate_combined_investment(
            request.initial_amount,
            request.monthly_investment,
            request.annual_rate,
            request.years
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Investment simulation completed successfully"
        }
        
    except ValueError as e:
        logger.error(f"Validation error in simulation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in investment simulation: {e}")
        raise HTTPException(status_code=500, detail="Failed to run investment simulation")

@router.post("/what-if")
async def simulate_what_if(request: WhatIfRequest):
    """
    Compare multiple investment scenarios
    """
    try:
        result = simulation_service.calculate_what_if_scenarios(
            request.initial_amount,
            request.monthly_investment,
            request.scenarios
        )
        
        return {
            "success": True,
            "data": result,
            "message": "What-if scenarios comparison completed successfully"
        }
        
    except ValueError as e:
        logger.error(f"Validation error in what-if simulation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in what-if simulation: {e}")
        raise HTTPException(status_code=500, detail="Failed to run what-if simulation")

@router.post("/goal-projection")
async def project_goal(request: GoalProjectionRequest):
    """
    Calculate time needed to reach a financial goal
    """
    try:
        result = simulation_service.calculate_goal_projection(
            request.target_amount,
            request.current_amount,
            request.monthly_contribution,
            request.annual_rate
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Goal projection completed successfully"
        }
        
    except ValueError as e:
        logger.error(f"Validation error in goal projection: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in goal projection: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate goal projection")

@router.get("/scenarios/examples")
async def get_example_scenarios():
    """
    Get example what-if scenarios for common investment goals
    """
    try:
        examples = [
            {
                "name": "Conservative",
                "annual_rate": 0.06,
                "years": 10
            },
            {
                "name": "Moderate",
                "annual_rate": 0.08,
                "years": 10
            },
            {
                "name": "Aggressive",
                "annual_rate": 0.12,
                "years": 10
            },
            {
                "name": "Long-term Conservative",
                "annual_rate": 0.06,
                "years": 20
            },
            {
                "name": "Long-term Moderate",
                "annual_rate": 0.08,
                "years": 20
            },
            {
                "name": "Long-term Aggressive",
                "annual_rate": 0.12,
                "years": 20
            }
        ]
        
        return {
            "success": True,
            "data": examples,
            "message": "Example scenarios retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting example scenarios: {e}")
        raise HTTPException(status_code=500, detail="Failed to get example scenarios")

@router.get("/calculator/help")
async def get_calculator_help():
    """
    Get help information for the simulation calculator
    """
    try:
        help_info = {
            "parameters": {
                "initial_amount": {
                    "description": "One-time investment amount at the start",
                    "example": 100000,
                    "notes": "Should be greater than 0"
                },
                "monthly_investment": {
                    "description": "Fixed amount invested every month",
                    "example": 5000,
                    "notes": "Should be greater than 0"
                },
                "annual_rate": {
                    "description": "Expected yearly return rate",
                    "example": 0.08,
                    "notes": "Use decimal format (8% = 0.08)"
                },
                "years": {
                    "description": "Investment duration in years",
                    "example": 10,
                    "notes": "Should be between 1 and 50 years"
                }
            },
            "formulas": {
                "compound_interest": "A = P(1 + r/n)^(nt)",
                "sip_future_value": "FV = P × [(1 + r)^n - 1] / r × (1 + r)",
                "notes": [
                    "P = Principal/Initial amount",
                    "r = Annual interest rate",
                    "n = Number of times interest is compounded per year",
                    "t = Time in years",
                    "FV = Future Value"
                ]
            },
            "assumptions": [
                "Returns are compounded monthly",
                "Monthly investments are made at the end of each month",
                "Inflation is not considered in calculations",
                "Taxes are not deducted from returns"
            ]
        }
        
        return {
            "success": True,
            "data": help_info,
            "message": "Calculator help retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting calculator help: {e}")
        raise HTTPException(status_code=500, detail="Failed to get calculator help")
