"""應用程式設定：從環境變數 / .env 讀取。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 資料庫
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/drama"
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP 業務規則
    OPT_CODE_LENGTH: int = 6
    OTP_TTL_SECONDS: int = 300          # 驗證碼有效 5 分鐘
    OTP_COOLDOWN_SECONDS: int = 60      # 同號碼 60 秒冷卻
    OTP_DAILY_LIMIT: int = 5            # 每號碼每日上限 5 次


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
