from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class RiskProfile(enum.Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class KYCStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class GoalCategory(enum.Enum):
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME = "home"
    VACATION = "vacation"
    EMERGENCY = "emergency"
    OTHER = "other"

class InvestmentType(enum.Enum):
    STOCK = "stock"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    BOND = "bond"
    CRYPTO = "crypto"

class TransactionType(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    risk_profile = Column(Enum(RiskProfile), default=RiskProfile.MODERATE)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    goals = relationship("Goal", back_populates="user")
    investments = relationship("Investment", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=False)
    monthly_contribution = Column(Float, default=0.0)
    category = Column(Enum(GoalCategory), default=GoalCategory.OTHER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(InvestmentType), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="investments")
    transactions = relationship("Transaction", back_populates="investment")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    investment = relationship("Investment", back_populates="transactions")
