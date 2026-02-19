"""
Application configuration using Pydantic Settings.
All values are loaded from environment variables / .env file.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────
    APP_NAME: str = "School Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ── Server ───────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Security ─────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Cloud Sync ───────────────────────────────────────
    CLOUD_API_URL: Optional[str] = None
    CLOUD_PING_URL: Optional[str] = None
    SYNC_SECRET_TOKEN: Optional[str] = None
    SYNC_INTERVAL_MINUTES: int = 5
    ENABLE_SYNC: bool = False

    # ── File Storage ─────────────────────────────────────
    MEDIA_ROOT: str = "./media"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # ── School Info ──────────────────────────────────────
    SCHOOL_NAME: str = "Greenfield High School"
    SCHOOL_ADDRESS: str = "123 Education Street"
    SCHOOL_PHONE: str = ""
    SCHOOL_EMAIL: str = ""
    SCHOOL_LOGO_PATH: str = "./media/school_logo.png"
    CURRENT_ACADEMIC_YEAR: int = 2024
    CURRENT_TERM: str = "Term 1"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def parse_image_types(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — only loaded once."""
    return Settings()


settings = get_settings()