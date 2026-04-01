"""
Database initialization script.
Run this script to create all database tables.

Usage:
    python init_db.py
"""

import asyncio
import logging
from src.database.base import Base
from src.database.sessionmaker import engine
from src.logger.custom_logger import logger

# Import all models to register them with Base metadata
from src.models.DatabaseModels import (
    OrganizationModel,
    UserModel,
    SubscriptionsModel,
    PaymentsModel,
    PatientModel,
    ScanModel,
    DetectionModel,
    RecommendationModel,
    ReportModel,
    ScanUsageModel
)


async def init_db():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Starting database initialization...")
        async with engine.begin() as conn:
            logger.info("Creating all database tables...")
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database tables created successfully!")
        logger.info("Database initialization completed.")
    except Exception as e:
        logger.error(f"✗ Error initializing database: {str(e)}", exc_info=True)
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
