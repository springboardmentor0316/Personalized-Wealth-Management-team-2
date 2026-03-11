from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import RiskProfile, KYCStatus, GoalCategory, InvestmentType, TransactionType

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    risk_profile: RiskProfile = RiskProfile.MODERATE
    kyc_status: KYCStatus = KYCStatus.PENDING

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    risk_profile: Optional[RiskProfile] = None
    kyc_status: Optional[KYCStatus] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0.0
    target_date: datetime
    monthly_contribution: float = 0.0
    category: GoalCategory = GoalCategory.OTHER

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    monthly_contribution: Optional[float] = None
    category: Optional[GoalCategory] = None

class Goal(GoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InvestmentBase(BaseModel):
    symbol: str
    name: str
    type: InvestmentType
    quantity: float
    average_cost: float
    current_price: float

class InvestmentCreate(InvestmentBase):
    pass

class Investment(InvestmentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    investment_id: int
    type: TransactionType
    quantity: float
    price: float
    amount: float
    date: datetime

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: User

class TokenRefresh(BaseModel):
    access_token: str
    token_type: str
