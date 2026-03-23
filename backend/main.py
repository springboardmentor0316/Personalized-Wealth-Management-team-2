from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import models
from models_pkg.market import MarketPrice  # Import market model directly
import schemas
import auth
from database import SessionLocal, engine
from dotenv import load_dotenv
from routes.market import router as market_router
from routes.simulation import router as simulation_router

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wealth Management API", version="1.0.0")

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = auth.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.id == payload.get("user_id")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

@app.post("/api/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        risk_profile=user.risk_profile,
        kyc_status=user.kyc_status
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"user_id": user.id})
    refresh_token = auth.create_refresh_token(data={"user_id": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": schemas.User.from_orm(user)
    }

@app.post("/api/auth/refresh")
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = auth.decode_refresh_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user = db.query(models.User).filter(models.User.id == payload.get("user_id")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    access_token = auth.create_access_token(data={"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/users/profile", response_model=schemas.User)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/api/users/profile", response_model=schemas.User)
def update_profile(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/api/goals", response_model=list[schemas.Goal])
def get_goals(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return goals

@app.post("/api/goals", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_goal = models.Goal(
        user_id=current_user.id,
        title=goal.title,
        description=goal.description,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        monthly_contribution=goal.monthly_contribution,
        category=goal.category
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.get("/api/goals/{goal_id}", response_model=schemas.Goal)
def get_goal(goal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.put("/api/goals/{goal_id}", response_model=schemas.Goal)
def update_goal(goal_id: int, goal_update: schemas.GoalUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    return goal

@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}

@app.get("/api/investments", response_model=list[schemas.Investment])
def get_investments(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.query(models.Investment).filter(models.Investment.user_id == current_user.id).all()
    return investments

@app.post("/api/investments", response_model=schemas.Investment)
def create_investment(investment: schemas.InvestmentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_investment = models.Investment(
        user_id=current_user.id,
        symbol=investment.symbol,
        name=investment.name,
        type=investment.type,
        quantity=investment.quantity,
        average_cost=investment.average_cost,
        current_price=investment.current_price
    )
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment

@app.get("/api/transactions", response_model=list[schemas.Transaction])
def get_transactions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()
    return transactions

@app.post("/api/transactions", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_transaction = models.Transaction(
        user_id=current_user.id,
        investment_id=transaction.investment_id,
        type=transaction.type,
        quantity=transaction.quantity,
        price=transaction.price,
        amount=transaction.amount,
        date=transaction.date
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/api/portfolio")
def get_portfolio(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.query(models.Investment).filter(models.Investment.user_id == current_user.id).all()
    
    portfolio = []
    total_value = 0
    total_cost = 0
    
    for investment in investments:
        current_value = investment.quantity * investment.current_price
        cost_basis = investment.quantity * investment.average_cost
        gain_loss = current_value - cost_basis
        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        portfolio.append({
            "id": investment.id,
            "symbol": investment.symbol,
            "name": investment.name,
            "type": investment.type,
            "quantity": investment.quantity,
            "average_cost": investment.average_cost,
            "current_price": investment.current_price,
            "current_value": current_value,
            "cost_basis": cost_basis,
            "gain_loss": gain_loss,
            "gain_loss_percent": gain_loss_percent
        })
        
        total_value += current_value
        total_cost += cost_basis
    
    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return {
        "investments": portfolio,
        "summary": {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent
        }
    }

# Include new routers
app.include_router(market_router)
app.include_router(simulation_router)

# Celery task endpoints (simplified without Redis dependency)
@app.get("/tasks/status")
async def get_task_status():
    """Get task status (simplified version)"""
    try:
        return {
            "celery_status": "disabled",
            "message": "Celery is disabled. Using synchronous task execution.",
            "market_update_available": True,
            "note": "Use /tasks/market-update for direct market price updates."
        }
    except Exception as e:
        return {
            "celery_status": "error",
            "error": str(e),
            "message": "Failed to get task status"
        }

@app.post("/tasks/market-update")
async def trigger_market_update(symbols: Optional[str] = None):
    """Trigger manual market price update"""
    try:
        # Direct execution without Celery for now
        from services.market_service import market_service
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            if symbols:
                symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
            else:
                # Default symbols if none provided
                symbol_list = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA", "BTC-USD", "ETH-USD"]
            
            # Fetch and store prices directly
            fetched_prices = market_service.fetch_real_time_prices(symbol_list)
            stored_count = market_service.store_prices(db, fetched_prices)
            
            return {
                "success": True,
                "message": f"Market update completed: {stored_count} prices updated",
                "symbols": symbol_list,
                "prices": fetched_prices
            }
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update market prices: {str(e)}")

@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    """Get result of a specific task (simplified version)"""
    try:
        # Return a simple response since we're not using Celery for now
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "Task execution is now synchronous. Use /tasks/market-update for direct updates.",
            "ready": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task result: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
