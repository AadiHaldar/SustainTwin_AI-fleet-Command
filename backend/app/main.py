"""SustainTwin AI -- FastAPI application entry point."""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base, engine, get_db

# Import routers
from app.api import auth, telemetry, diagnostics
from app.api.websocket import router as ws_router

settings = get_settings()

app = FastAPI(
    title="SustainTwin AI API",
    description="Backend API for SustainTwin Agentic Edge Intelligence Platform",
    version=settings.VERSION,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(telemetry.router, prefix=f"{settings.API_V1_STR}/telemetry", tags=["Telemetry"])
app.include_router(diagnostics.router, prefix=f"{settings.API_V1_STR}/diagnostics", tags=["Diagnostics"])
app.include_router(ws_router, tags=["WebSocket"])

# ---------------------------------------------------------------------------
# Startup: ensure all tables exist
# ---------------------------------------------------------------------------

@app.on_event("startup")
def create_tables() -> None:
    # Import all models so SQLAlchemy sees them before create_all
    import app.models.machine   # noqa: F401
    import app.models.user      # noqa: F401
    import app.models.diagnosis  # noqa: F401

    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Health-check endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SustainTwin AI API",
        "version": settings.VERSION,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).scalar_one()
        connected = result == 1
    except Exception:
        connected = False

    backend = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"

    return {
        "status": "ok" if connected else "degraded",
        "database": backend,
        "connected": connected,
    }
