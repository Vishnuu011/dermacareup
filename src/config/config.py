from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional
import os, sys
from pathlib import Path



load_dotenv(
    Path(__file__).parent.parent.parent / ".env"
)

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Email SMTP Configuration (Optional)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    # Serper.dev API Configuration
    SERPER_API_KEY: Optional[str] = ""
    
    # Stripe Configuration
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLIC_KEY: str 
    STRIPE_WEBHOOK_SECRET: str

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        env_file = ".env"


settings = Settings()    