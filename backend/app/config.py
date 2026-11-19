import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/ directory
PROJECT_ROOT = BASE_DIR.parent                     # women safety agent/ root

# Resolve .env or .env.local file location
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = PROJECT_ROOT / ".env"
if not env_path.exists():
    env_path = PROJECT_ROOT / ".env.local"

DEFAULT_DB_PATH = (PROJECT_ROOT / "safety_agent.db").as_posix()
DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path) if env_path.exists() else None,
        extra="ignore"
    )

    PROJECT_NAME: str = "Women's Travel Safety & Companion Matching"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = DEFAULT_SQLITE_URL

    @property
    def canonical_database_url(self) -> str:
        """Ensures relative SQLite paths always resolve to the canonical project database."""
        if self.DATABASE_URL.startswith("sqlite:///./"):
            rel_file = self.DATABASE_URL.replace("sqlite:///./", "")
            return f"sqlite:///{(PROJECT_ROOT / rel_file).as_posix()}"
        return self.DATABASE_URL
    
    # Security
    SECRET_KEY: str = "dev_secret_key_super_secure_safety_agent_women_travel_2026_xyz"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # External APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = ""
    LOCATIONIQ_API_KEY: Optional[str] = ""
    
    # Safety & Deviation Thresholds
    DEVIATION_DISTANCE_THRESHOLD_METERS: float = 150.0
    DEVIATION_PERSISTENCE_COUNT: int = 3
    DEVIATION_TIMEOUT_SECONDS: int = 60
    GPS_ACCURACY_THRESHOLD_METERS: float = 50.0

settings = Settings()
