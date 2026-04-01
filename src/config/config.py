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

    class Config:
        env_file = ".env"


settings = Settings()    