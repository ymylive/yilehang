"""Application settings."""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


INSECURE_SECRET_KEY_VALUES = {
    "your-secret-key-change-in-production",
    "change-this-in-production",
    "change-this-to-a-random-string",
}


class Settings(BaseSettings):
    """App settings."""

    # Basic
    PROJECT_NAME: str = "韧翎成长计划"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str  # Required: Must be set via environment variable
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2  # 2 hours (reduced from 7 days)
    ALGORITHM: str = "HS256"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        secret_key = (self.SECRET_KEY or "").strip()
        if (
            not secret_key
            or secret_key in INSECURE_SECRET_KEY_VALUES
            or secret_key.lower().startswith("yilehang-secret")
        ):
            raise ValueError(
                "SECRET_KEY must be set via environment variable. "
                "Generate one with: openssl rand -hex 32"
            )

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
    DEV_PRINT_CODE_ON_SEND_FAIL: bool = False

    # Business rules
    COACH_DEFAULT_COMMISSION_RATE: float = 0.7  # 70%
    BOOKING_CANCEL_HOURS_BEFORE: int = 2

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()

