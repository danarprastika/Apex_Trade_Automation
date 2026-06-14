from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "APEX Financial Intelligence Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    DATABASE_URL: str = "postgresql+psycopg2://apex:apex_password@postgres:5432/apex_db"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET_KEY: str = "CHANGE_THIS_SECRET_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15

    TELEGRAM_BOT_TOKEN: str = ""
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""

    IS_LIVE_TRADING: bool = False
    ENCRYPTION_KEY: str = ""

    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"


settings = Settings()
