from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.models import User, Transaction
from schemas.schemas import TransactionCreate, TransactionOut
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=list[TransactionOut])
async def list_transactions(
    symbol: Optional[str] = Query(None),
    type_filter: Optional[str] = Query(None, alias="type"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(Transaction.executed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if symbol:
        q = q.where(Transaction.symbol == symbol.upper())
    if type_filter:
        q = q.where(Transaction.type == type_filter)

    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    if not data.get("executed_at"):
        data["executed_at"] = datetime.utcnow()

    txn = Transaction(**data, user_id=current_user.id)
    db.add(txn)
    await db.flush()
    await db.refresh(txn)
    return txn


@router.get("/{txn_id}", response_model=TransactionOut)
async def get_transaction(
    txn_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    txn_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == current_user.id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    await db.delete(txn)