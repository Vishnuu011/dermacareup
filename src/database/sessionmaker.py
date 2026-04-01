import ssl

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.config.config import settings
from src.database.base import Base
import os, sys
from pathlib import Path


ssl_context = ssl.create_default_context()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)

async_session= sessionmaker(
    engine, class_=AsyncSession, 
    expire_on_commit=False
)