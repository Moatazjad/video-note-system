from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Video Note System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    DATABASE_URL: str
    REDIS_URL: str

    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    LOG_DIR: Path = BASE_DIR / "logs"
    FONT_DIR: Path = BASE_DIR / "fonts"

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
