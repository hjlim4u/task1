import aioredis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import logging

# Database configuration
DATABASE_URL = "sqlite:///./code_reviews.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis configuration
REDIS_URL = "redis://localhost:6379"
redis_client = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logging.info("Redis connection established")
    except Exception as e:
        logging.error(f"Failed to connect to Redis: {e}")
        redis_client = None

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)