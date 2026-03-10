import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime,
    ForeignKey, Enum, Text, JSON, func
)
from sqlalchemy.orm import relationship
from db.database import Base


# ── Enums ────────────────────────────────────────────────────
class RiskProfileEnum(str, enum.Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"

class KYCStatusEnum(str, enum.Enum):
    unverified = "unverified"
    verified = "verified"

class GoalTypeEnum(str, enum.Enum):
    retirement = "retirement"
    home = "home"
    education = "education"
    custom = "custom"

class GoalStatusEnum(str, enum.Enum):
    active = "active"
    paused = "paused"
    completed = "completed"

class AssetTypeEnum(str, enum.Enum):
    stock = "stock"
    etf = "etf"
    mutual_fund = "mutual_fund"
    bond = "bond"
    cash = "cash"

class TransactionTypeEnum(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    dividend = "dividend"
    contribution = "contribution"
    withdrawal = "withdrawal"


# ── ORM Models ───────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(120), nullable=False)
    email        = Column(String(255), nullable=False, unique=True, index=True)
    password     = Column(String(255), nullable=False)
    risk_profile = Column(Enum(RiskProfileEnum), nullable=False, default=RiskProfileEnum.moderate)
    kyc_status   = Column(Enum(KYCStatusEnum), nullable=False, default=KYCStatusEnum.unverified)
    created_at   = Column(DateTime, server_default=func.now())

    goals           = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    investments     = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    transactions    = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    simulations     = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id                   = Column(Integer, primary_key=True, index=True)
    user_id              = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_type            = Column(Enum(GoalTypeEnum), nullable=False)
    target_amount        = Column(Numeric(15, 2), nullable=False)
    target_date          = Column(Date, nullable=False)
    monthly_contribution = Column(Numeric(12, 2), nullable=False, default=0)
    status               = Column(Enum(GoalStatusEnum), nullable=False, default=GoalStatusEnum.active)
    created_at           = Column(DateTime, server_default=func.now())

    user        = relationship("User", back_populates="goals")
    simulations = relationship("Simulation", back_populates="goal")


class Investment(Base):
    __tablename__ = "investments"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    asset_type    = Column(Enum(AssetTypeEnum), nullable=False)
    symbol        = Column(String(20), nullable=False, index=True)
    units         = Column(Numeric(18, 6), nullable=False)
    avg_buy_price = Column(Numeric(15, 4), nullable=False)
    cost_basis    = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=False, default=0)
    last_price    = Column(Numeric(15, 4), nullable=False, default=0)
    last_price_at = Column(DateTime)

    user = relationship("User", back_populates="investments")


class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol      = Column(String(20), nullable=False, index=True)
    type        = Column(Enum(TransactionTypeEnum), nullable=False)
    quantity    = Column(Numeric(18, 6), nullable=False)
    price       = Column(Numeric(15, 4), nullable=False)
    fees        = Column(Numeric(10, 2), nullable=False, default=0)
    executed_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="transactions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id                   = Column(Integer, primary_key=True)
    user_id              = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title                = Column(String(255), nullable=False)
    recommendation_text  = Column(Text)
    suggested_allocation = Column(JSON)
    created_at           = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="recommendations")


class Simulation(Base):
    __tablename__ = "simulations"

    id            = Column(Integer, primary_key=True)
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id       = Column(Integer, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    scenario_name = Column(String(120), nullable=False)
    assumptions   = Column(JSON)
    results       = Column(JSON)
    created_at    = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="simulations")
    goal = relationship("Goal", back_populates="simulations")