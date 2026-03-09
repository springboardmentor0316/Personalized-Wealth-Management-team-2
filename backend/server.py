from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import enum

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./wealth_management.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class RiskTolerance(str, enum.Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"

class KYCStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    risk_tolerance = Column(Enum(RiskTolerance), default=RiskTolerance.moderate)
    investment_horizon = Column(Integer, default=5)
    annual_income = Column(Integer, nullable=True)
    kyc_status = Column(Enum(KYCStatus), default=KYCStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0)
    monthly_contribution = Column(Float)
    target_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Wealth Management API")

# CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Wealth Management API",
        "endpoints": [
            "GET  /health",
            "POST /register",
            "POST /login",
            "POST /refresh",
            "GET  /users",
            "GET  /profile",
            "GET  /goals",
            "POST /goals",
            "PUT  /goals/{id}",
            "DELETE /goals/{id}"
        ]
    }

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    risk_tolerance: Optional[str] = "moderate"
    investment_horizon: Optional[int] = 5
    annual_income: Optional[int] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshToken(BaseModel):
    refresh_token: str

class GoalCreate(BaseModel):
    title: str
    target_amount: float
    monthly_contribution: float
    target_date: datetime

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    monthly_contribution: Optional[float] = None
    target_date: Optional[datetime] = None

# Helper functions
def verify_password(plain_password, hashed_password):
    # Handle plain text passwords stored with "plain:" prefix
    if hashed_password.startswith("plain:"):
        return plain_password == hashed_password[6:]
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Last fallback - direct comparison
        return plain_password == hashed_password

def get_password_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback for demo - store with prefix
        return f"plain:{password}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Routes
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        print(f"Registration attempt: {user_data.email}")
        
        # Validation
        if not user_data.full_name or not user_data.email or not user_data.password:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="User already registered")
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password=hashed_password,
            risk_tolerance=RiskTolerance(user_data.risk_tolerance) if user_data.risk_tolerance else RiskTolerance.moderate,
            investment_horizon=user_data.investment_horizon or 5,
            annual_income=user_data.annual_income,
            kyc_status=KYCStatus.pending
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"User registered successfully: {user_data.email}")
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "email": new_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Registration error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "full_name": user.full_name},
        expires_delta=timedelta(hours=24)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=Token)
def refresh_token(refresh_data: RefreshToken):
    try:
        payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        email = payload.get("sub")
        user_id = payload.get("id")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": email, "id": user_id},
            expires_delta=timedelta(hours=24)
        )
        new_refresh_token = create_refresh_token(
            data={"sub": email, "id": user_id}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/profile")
def get_profile(db: Session = Depends(get_db)):
    # For demo, return first user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "risk_tolerance": user.risk_tolerance.value if user.risk_tolerance else None,
        "investment_horizon": user.investment_horizon,
        "annual_income": user.annual_income,
        "kyc_status": user.kyc_status.value if user.kyc_status else None,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "risk_tolerance": user.risk_tolerance.value if user.risk_tolerance else None,
        "investment_horizon": user.investment_horizon,
        "annual_income": user.annual_income,
        "kyc_status": user.kyc_status.value if user.kyc_status else None,
        "created_at": user.created_at.isoformat() if user.created_at else None
    } for user in users]

# Goals CRUD endpoints
@app.post("/goals")
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_goal = Goal(
        user_id=user.id,
        title=goal.title,
        target_amount=goal.target_amount,
        monthly_contribution=goal.monthly_contribution,
        target_date=goal.target_date,
        current_amount=0
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return {
        "id": db_goal.id,
        "title": db_goal.title,
        "target_amount": db_goal.target_amount,
        "current_amount": db_goal.current_amount,
        "monthly_contribution": db_goal.monthly_contribution,
        "target_date": db_goal.target_date.isoformat() if db_goal.target_date else None,
        "created_at": db_goal.created_at.isoformat() if db_goal.created_at else None
    }

@app.get("/goals")
def get_goals(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        return []
    
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    return [{
        "id": goal.id,
        "title": goal.title,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "monthly_contribution": goal.monthly_contribution,
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "created_at": goal.created_at.isoformat() if goal.created_at else None
    } for goal in goals]

@app.put("/goals/{goal_id}")
def update_goal(goal_id: int, goal_update: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if goal_update.title is not None:
        goal.title = goal_update.title
    if goal_update.target_amount is not None:
        goal.target_amount = goal_update.target_amount
    if goal_update.current_amount is not None:
        goal.current_amount = goal_update.current_amount
    if goal_update.monthly_contribution is not None:
        goal.monthly_contribution = goal_update.monthly_contribution
    if goal_update.target_date is not None:
        goal.target_date = goal_update.target_date
    
    db.commit()
    db.refresh(goal)
    return {
        "id": goal.id,
        "title": goal.title,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "monthly_contribution": goal.monthly_contribution,
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "created_at": goal.created_at.isoformat() if goal.created_at else None
    }

@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://localhost:5050")
    print("API endpoints:")
    print("  GET  /health   - Health check")
    print("  POST /register - User registration")
    print("  POST /login    - User login")
    print("  POST /refresh  - Refresh token")
    print("  GET  /profile  - Get user profile")
    print("  GET  /users    - Get all users")
    print("  GET  /goals    - Get goals")
    print("  POST /goals    - Create goal")
    print("  PUT  /goals/{id} - Update goal")
    print("  DELETE /goals/{id} - Delete goal")
    uvicorn.run(app, host="0.0.0.0", port=5050)
