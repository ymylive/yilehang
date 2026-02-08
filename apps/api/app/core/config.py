"""Application settings."""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings."""

    # Basic
    PROJECT_NAME: str = "Yilehang ITS Sports Platform"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/yilehang"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # WeChat Mini Program
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    ALLOW_WECHAT_LOGIN_WITHOUT_SECRET: bool = False

    # Email SMTP (Gmail)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_SSL: bool = False

    # Dev mode: print verification code to console instead of sending email
    DEV_PRINT_CODE: bool = False
    # If SMTP fails, still keep code available for dev/test flows
    DEV_PRINT_CODE_ON_SEND_FAIL: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
