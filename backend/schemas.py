from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    risk_profile: Optional[str] = "moderate"
    kyc_status: Optional[str] = "pending"

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    risk_profile: Optional[str] = None

class User(UserBase):
    id: int
    risk_profile: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Goal schemas
class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    time_horizon: int
    description: Optional[str] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    time_horizon: Optional[int] = None
    description: Optional[str] = None

class Goal(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Investment schemas
class InvestmentBase(BaseModel):
    symbol: str
    quantity: float
    average_cost: float

class InvestmentCreate(InvestmentBase):
    name: str
    type: str
    current_price: float

class Investment(InvestmentBase):
    id: int
    user_id: int
    name: str
    type: str
    current_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    symbol: str
    transaction_type: str  # 'buy' or 'sell'
    quantity: float
    price: float

class TransactionCreate(TransactionBase):
    investment_id: int
    amount: float
    date: datetime
    fees: float = 0.0

class Transaction(TransactionBase):
    id: int
    user_id: int
    investment_id: int
    amount: float
    fees: float
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Market data schemas
class MarketPriceResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    timestamp: datetime

# Simulation schemas
class SimulationRequest(BaseModel):
    initial_amount: float
    monthly_contribution: float
    expected_return: float
    time_period: int

class SimulationResult(BaseModel):
    final_amount: float
    total_contributions: float
    total_returns: float

class WhatIfRequest(BaseModel):
    scenario: str
    parameters: dict

class GoalProjectionRequest(BaseModel):
    goal_id: int
    current_amount: float
    monthly_contribution: float
    expected_return: float

# Analytics schemas
class PerformanceMetrics(BaseModel):
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    benchmark_return: float
    excess_return: float

class FinancialHealth(BaseModel):
    overall_score: float
    grade: str
    status: str
    individual_scores: dict
    recommendations: List[str]

# Alert schemas
class AlertCreate(BaseModel):
    alert_type: str
    symbol: Optional[str] = None
    condition: str
    threshold_value: float
    notification_method: str = "email"
    frequency: str = "once"

class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    symbol: Optional[str] = None
    condition: Optional[str] = None
    threshold_value: Optional[float] = None
    notification_method: Optional[str] = None
    frequency: Optional[str] = None
    is_active: Optional[bool] = None

# Recommendation schemas
class RecommendationResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    reasoning: Optional[str] = None
    suggested_symbols: Optional[List[str]] = []
    expected_return: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = None

# Chart schemas
class ChartDataResponse(BaseModel):
    type: str
    data: Optional[dict] = None
    metadata: Optional[dict] = None

# Calculator request schemas
class SIPCalculatorRequest(BaseModel):
    monthly_investment: float
    expected_return: float
    time_period_years: int

class RetirementCalculatorRequest(BaseModel):
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    expected_return: float
    inflation_rate: float

class LoanPayoffRequest(BaseModel):
    principal: float
    interest_rate: float
    loan_term_years: int
    extra_payment: float = 0
