import json
from pydantic_settings import BaseSettings
from pydantic import Field
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

    # A plain `str` field (not List[str]) so pydantic-settings never tries
    # to auto-JSON-decode the raw env var before our own parsing runs --
    # that auto-decode happens at the settings-SOURCE level, before any
    # field_validator gets a chance to run, and crashes on a plain
    # comma-separated value like "http://localhost:3000" (only a
    # JSON-array-bracketed string would have survived it). Accepts either
    # a JSON array string or a comma-separated string.
    CORS_ORIGINS_RAW: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    DATABASE_URL: str
    REDIS_URL: str

    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    MAX_VIDEO_DURATION_SECONDS: int = 7200

    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    LOG_DIR: Path = BASE_DIR / "logs"
    FONT_DIR: Path = BASE_DIR / "fonts"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        value = self.CORS_ORIGINS_RAW.strip()
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True
        populate_by_name = True


settings = Settings()
