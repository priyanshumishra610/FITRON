"""
FITRON Database Configuration
PostgreSQL and MongoDB connections
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging
from typing import AsyncGenerator

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# SQLAlchemy setup for PostgreSQL
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for SQLAlchemy models
Base = declarative_base()

# MongoDB setup
mongo_client: AsyncIOMotorClient = None
mongo_db = None

async def init_db():
    """Initialize database connections"""
    global mongo_client, mongo_db
    
    try:
        # Initialize MongoDB
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongo_db = mongo_client.fitron
        logger.info("✅ MongoDB connected successfully")
        
        # Test PostgreSQL connection
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ PostgreSQL connected and tables created")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def get_mongo_db():
    """Get MongoDB database instance"""
    return mongo_db

async def close_db():
    """Close database connections"""
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")
    
    await engine.dispose()
    logger.info("PostgreSQL connection closed")

# Database collections for MongoDB
class Collections:
    """MongoDB collection names"""
    REP_LOGS = "rep_logs"
    POSE_DATA = "pose_data"
    PHYSIQUE_GOALS = "physique_goals"
    WORKOUT_SESSIONS = "workout_sessions"
    USER_METRICS = "user_metrics"
    AI_FEEDBACK = "ai_feedback"
    TRAINER_NOTES = "trainer_notes"
    ZENML_PIPELINES = "zenml_pipelines" 