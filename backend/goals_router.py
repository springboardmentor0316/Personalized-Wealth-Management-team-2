from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.database import get_db
from models.models import User, Goal, Transaction
from schemas.schemas import GoalCreate, GoalUpdate, GoalOut, GoalProgress
from auth import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])


def _calc_progress(goal: Goal) -> GoalProgress:
    """Attach derived progress fields to a Goal ORM object."""
    today = date.today()
    months_left = max(
        0,
        (goal.target_date.year - today.year) * 12 + (goal.target_date.month - today.month)
    )
    # Approximate saved as fraction of contributions made since creation
    months_elapsed = max(0, (today.year - goal.created_at.year) * 12 + (today.month - goal.created_at.month))
    saved = Decimal(months_elapsed) * goal.monthly_contribution
    target = goal.target_amount or Decimal("1")
    progress_pct = float(min(100, (saved / target) * 100))
    projected = saved + Decimal(months_left) * goal.monthly_contribution
    on_track = projected >= goal.target_amount

    out = GoalProgress.model_validate(goal)
    out.saved = saved
    out.progress_pct = round(progress_pct, 1)
    out.months_remaining = months_left
    out.projected_value = projected
    out.on_track = on_track
    return out


@router.get("/", response_model=list[GoalProgress])
async def list_goals(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.created_at.desc())
    if status_filter:
        q = q.where(Goal.status == status_filter)
    result = await db.execute(q)
    goals = result.scalars().all()
    return [_calc_progress(g) for g in goals]


@router.post("/", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = Goal(**payload.model_dump(), user_id=current_user.id)
    db.add(goal)
    await db.flush()
    await db.refresh(goal)
    return goal


@router.get("/{goal_id}", response_model=GoalProgress)
async def get_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return _calc_progress(goal)


@router.patch("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(goal, field, value)

    await db.flush()
    await db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    await db.delete(goal)


@router.patch("/{goal_id}/status", response_model=GoalOut)
async def toggle_goal_status(
    goal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    from models.models import GoalStatusEnum
    goal.status = (
        GoalStatusEnum.paused if goal.status == GoalStatusEnum.active else GoalStatusEnum.active
    )
    await db.flush()
    await db.refresh(goal)
    return goal