from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.models import User, Investment
from schemas.schemas import InvestmentCreate, InvestmentUpdate, InvestmentOut, PortfolioSummary
from auth import get_current_user

router = APIRouter(prefix="/investments", tags=["Portfolio"])


def _build_summary(investments: list[Investment]) -> PortfolioSummary:
    total_cost = sum(i.cost_basis for i in investments) or Decimal("0")
    total_val  = sum(i.current_value for i in investments) or Decimal("0")
    gain       = total_val - total_cost
    gain_pct   = float((gain / total_cost * 100)) if total_cost else 0.0

    alloc: dict[str, float] = {}
    for inv in investments:
        key = inv.asset_type.value if hasattr(inv.asset_type, "value") else str(inv.asset_type)
        alloc[key] = alloc.get(key, 0.0) + float(inv.current_value)
    if total_val:
        alloc = {k: round(v / float(total_val) * 100, 2) for k, v in alloc.items()}

    return PortfolioSummary(
        total_cost_basis=total_cost,
        total_current_value=total_val,
        total_gain_loss=gain,
        total_gain_loss_pct=round(gain_pct, 2),
        allocation_by_type=alloc,
        positions=[InvestmentOut.model_validate(i) for i in investments],
    )


@router.get("/", response_model=list[InvestmentOut])
async def list_investments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investment)
        .where(Investment.user_id == current_user.id)
        .order_by(Investment.id)
    )
    return result.scalars().all()


@router.get("/summary", response_model=PortfolioSummary)
async def portfolio_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investment).where(Investment.user_id == current_user.id)
    )
    investments = result.scalars().all()
    return _build_summary(investments)


@router.post("/", response_model=InvestmentOut, status_code=status.HTTP_201_CREATED)
async def create_investment(
    payload: InvestmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cost_basis = payload.units * payload.avg_buy_price
    inv = Investment(
        user_id=current_user.id,
        asset_type=payload.asset_type,
        symbol=payload.symbol,
        units=payload.units,
        avg_buy_price=payload.avg_buy_price,
        cost_basis=cost_basis,
        current_value=cost_basis,   # will be refreshed by market sync (Milestone 3)
        last_price=payload.avg_buy_price,
    )
    db.add(inv)
    await db.flush()
    await db.refresh(inv)
    return inv


@router.get("/{inv_id}", response_model=InvestmentOut)
async def get_investment(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investment).where(Investment.id == inv_id, Investment.user_id == current_user.id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    return inv


@router.patch("/{inv_id}", response_model=InvestmentOut)
async def update_investment(
    inv_id: int,
    payload: InvestmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investment).where(Investment.id == inv_id, Investment.user_id == current_user.id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(inv, field, value)

    # Recalculate cost basis
    inv.cost_basis = inv.units * inv.avg_buy_price

    await db.flush()
    await db.refresh(inv)
    return inv


@router.delete("/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Investment).where(Investment.id == inv_id, Investment.user_id == current_user.id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    await db.delete(inv)
