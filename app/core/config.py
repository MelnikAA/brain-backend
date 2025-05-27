from pydantic import BaseSettings, EmailStr, PostgresDsn, validator
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import secrets
from pathlib import Path

# Загружаем .env из папки app
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Brain Tumor Detection API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки базы данных
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "diplom-brain")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    # Настройки SMTP
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Настройки безопасности
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS настройки
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Настройки для загрузки файлов
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 