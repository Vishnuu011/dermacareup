from pydantic_settings import BaseSettings
from dotenv import load_dotenv
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

    class Config:
        env_file = ".env"


settings = Settings()    