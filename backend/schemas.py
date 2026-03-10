from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, field_validator
from models.models import (
    RiskProfileEnum, KYCStatusEnum, GoalTypeEnum, GoalStatusEnum,
    AssetTypeEnum, TransactionTypeEnum
)


# ── Auth ─────────────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    risk_profile: RiskProfileEnum = RiskProfileEnum.moderate

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    risk_profile: RiskProfileEnum
    kyc_status: KYCStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Goals ────────────────────────────────────────────────────
class GoalCreate(BaseModel):
    goal_type: GoalTypeEnum
    target_amount: Decimal
    target_date: date
    monthly_contribution: Decimal
    status: GoalStatusEnum = GoalStatusEnum.active

    @field_validator("target_amount")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("target_amount must be positive")
        return v

class GoalUpdate(BaseModel):
    goal_type: Optional[GoalTypeEnum] = None
    target_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
    monthly_contribution: Optional[Decimal] = None
    status: Optional[GoalStatusEnum] = None

class GoalOut(BaseModel):
    id: int
    user_id: int
    goal_type: GoalTypeEnum
    target_amount: Decimal
    target_date: date
    monthly_contribution: Decimal
    status: GoalStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}

class GoalProgress(GoalOut):
    saved: Decimal = Decimal("0")
    progress_pct: float = 0.0
    months_remaining: int = 0
    projected_value: Decimal = Decimal("0")
    on_track: bool = False


# ── Investments ──────────────────────────────────────────────
class InvestmentCreate(BaseModel):
    asset_type: AssetTypeEnum
    symbol: str
    units: Decimal
    avg_buy_price: Decimal

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, v):
        return v.upper().strip()

class InvestmentUpdate(BaseModel):
    asset_type: Optional[AssetTypeEnum] = None
    units: Optional[Decimal] = None
    avg_buy_price: Optional[Decimal] = None

class InvestmentOut(BaseModel):
    id: int
    user_id: int
    asset_type: AssetTypeEnum
    symbol: str
    units: Decimal
    avg_buy_price: Decimal
    cost_basis: Decimal
    current_value: Decimal
    last_price: Decimal
    last_price_at: Optional[datetime]

    model_config = {"from_attributes": True}

class PortfolioSummary(BaseModel):
    total_cost_basis: Decimal
    total_current_value: Decimal
    total_gain_loss: Decimal
    total_gain_loss_pct: float
    allocation_by_type: dict[str, float]
    positions: list[InvestmentOut]


# ── Transactions ─────────────────────────────────────────────
class TransactionCreate(BaseModel):
    symbol: str
    type: TransactionTypeEnum
    quantity: Decimal
    price: Decimal
    fees: Decimal = Decimal("0")
    executed_at: Optional[datetime] = None

    @field_validator("symbol")
    @classmethod
    def uppercase_symbol(cls, v):
        return v.upper().strip()

class TransactionOut(BaseModel):
    id: int
    user_id: int
    symbol: str
    type: TransactionTypeEnum
    quantity: Decimal
    price: Decimal
    fees: Decimal
    executed_at: datetime

    model_config = {"from_attributes": True}


# ── Generic ──────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    size: int