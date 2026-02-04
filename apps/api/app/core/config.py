"""
核心配置模块
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    PROJECT_NAME: str = "易乐航·ITS智慧体教云平台"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    ALGORITHM: str = "HS256"

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/yilehang"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # 微信小程序配置
    WECHAT_APPID: str = "wxdbd150a0458a3c7c"  # 小程序AppID
    WECHAT_SECRET: str = ""  # 小程序AppSecret
    WECHAT_APP_ID: str = ""  # 公众号AppID (如有)
    WECHAT_APP_SECRET: str = ""  # 公众号AppSecret

    # 阿里云OSS配置
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_OSS_BUCKET: str = ""
    ALIYUN_OSS_ENDPOINT: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
