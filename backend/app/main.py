from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, telemetry
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base, engine, get_db

app = FastAPI(
    title="SustainTwin AI API",
    description="Backend API for SustainTwin Agentic Edge Intelligence Platform",
    version="1.0.0"
)

settings = get_settings()

# CORS configuration
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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])

@app.on_event("startup")
def create_tables() -> None:
    import app.models.machine  # noqa: F401

    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to SustainTwin AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar_one()
    backend = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"

    return {
        "status": "ok" if result == 1 else "degraded",
        "database": backend,
        "connected": result == 1,
    }
