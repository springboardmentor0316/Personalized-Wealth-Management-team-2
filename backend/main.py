from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from db.database import engine, Base
from auth import get_current_user
from routers import auth_router, goals_router, investments_router, transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="Wealth Management API — Milestone 2: Goals & Portfolio Core",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth_router.router,         prefix="/api/v1")
app.include_router(goals_router.router,        prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(investments_router.router,  prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(transactions_router.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])


@app.get("/health")
async def health():
    return {"status": "ok", "milestone": 2}