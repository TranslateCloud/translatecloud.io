from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_SECRET_ARN: str = "prod/translatecloud/db"
    AWS_REGION: str = "eu-west-1"
    
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_CLIENT_ID: Optional[str] = None
    COGNITO_REGION: str = "eu-west-1"
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "TranslateCloud API"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
