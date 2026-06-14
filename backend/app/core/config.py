from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "SustainTwin AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost,http://localhost:3000"

    # Database — Supabase PostgreSQL (no SQLite fallback)
    DATABASE_URL: str = "postgresql+psycopg2://sustain_user:sustain_password@localhost:5432/sustain_twin"

    # Redis — optional, caching disabled if empty
    REDIS_URL: str = ""

    # Auth
    SECRET_KEY: str = "dev-only-change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI
    GEMINI_API_KEY: str = ""

    # Sustainability
    IDLE_CO2_KG_PER_HR: float = 2.68  # EPA heavy machinery idle factor
    FUEL_CO2_KG_PER_LITER: float = 2.31  # diesel combustion factor

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
