from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "SustainTwin AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Use SQLite for local development to bypass Docker daemon issues
    DATABASE_URL: str = "sqlite:///./sustain_twin.db"
    
    GEMINI_API_KEY: str = ""
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
