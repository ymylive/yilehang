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
    WECHAT_APPID: str = "wxdbd150a0458a3c7c"
    WECHAT_SECRET: str = ""

    # Aliyun SMS
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = ""
    ALIYUN_SMS_TEMPLATE_CODE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
