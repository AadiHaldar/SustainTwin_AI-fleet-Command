from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, telemetry

app = FastAPI(
    title="SustainTwin AI API",
    description="Backend API for SustainTwin Agentic Edge Intelligence Platform",
    version="1.0.0"
)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to SustainTwin AI API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
