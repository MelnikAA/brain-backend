from pydantic_settings import BaseSettings
from pydantic import EmailStr, PostgresDsn, validator
from typing import Optional, Dict, Any, List, Union
import os
from dotenv import load_dotenv
import secrets
from pathlib import Path
from pydantic import AnyHttpUrl

# Загружаем .env из корневой директории проекта
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Predictions API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки базы данных
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "medical_predictions"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Настройки SMTP
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAILS_ENABLED: bool = False
    EMAIL_TEMPLATES_DIR: Path = Path(__file__).parent.parent / "email-templates"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    # Настройки безопасности
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
    
    # CORS настройки
    ALLOWED_ORIGINS: List[str] = ["https://braincheck-diplom.ru"]
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Настройки для загрузки файлов
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Настройки DeepSeek API
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")

    # Настройки OpenRouter API
    OPENROUTER_API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    SERVER_NAME: str = "braincheck-diplom.ru"
    SERVER_HOST: str = "https://braincheck-diplom.ru"
    FRONTEND_URL: str = "https://braincheck-diplom.ru"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    @validator("EMAILS_ENABLED", pre=True)
    def validate_email_settings(cls, v: bool, values: Dict[str, Any]) -> bool:
        if v:
            if not values.get("SMTP_HOST"):
                raise ValueError("SMTP_HOST must be set when EMAILS_ENABLED is True")
            if not values.get("SMTP_PORT"):
                raise ValueError("SMTP_PORT must be set when EMAILS_ENABLED is True")
            if not values.get("SMTP_USER"):
                raise ValueError("SMTP_USER must be set when EMAILS_ENABLED is True")
            if not values.get("SMTP_PASSWORD"):
                raise ValueError("SMTP_PASSWORD must be set when EMAILS_ENABLED is True")
            if not values.get("EMAILS_FROM_EMAIL"):
                raise ValueError("EMAILS_FROM_EMAIL must be set when EMAILS_ENABLED is True")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 