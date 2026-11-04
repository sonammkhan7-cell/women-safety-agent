import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Women's Travel Safety & Companion Matching"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./safety_agent.db"
    
    # Security
    SECRET_KEY: str = "dev_secret_key_super_secure_safety_agent_women_travel_2026_xyz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = ""
    
    # Safety & Deviation Thresholds
    DEVIATION_DISTANCE_THRESHOLD_METERS: float = 150.0
    DEVIATION_PERSISTENCE_COUNT: int = 3
    DEVIATION_TIMEOUT_SECONDS: int = 60
    GPS_ACCURACY_THRESHOLD_METERS: float = 50.0

settings = Settings()
