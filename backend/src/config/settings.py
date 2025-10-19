from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # AWS Configuration
    DATABASE_SECRET_ARN: str = "prod/translatecloud/db"
    AWS_REGION: str = "eu-west-1"

    # Cognito Authentication
    COGNITO_USER_POOL_ID: str = "eu-west-1_FH51nx4II"
    COGNITO_CLIENT_ID: str = "6he757k99vkr15llk139usiub6"
    COGNITO_REGION: str = "eu-west-1"

    # Stripe Payment Processing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Translation Services
    DEEPL_API_KEY: Optional[str] = None

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"

    # Database (local development only - use AWS Secrets Manager in production)
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Configuration
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "TranslateCloud API"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
_settings = None

def get_settings() -> Settings:
    """Get settings singleton instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Default instance for backward compatibility
settings = Settings()