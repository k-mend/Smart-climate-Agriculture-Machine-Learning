from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from .config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database Models
class PredictionLog(Base):
    """Store prediction logs for analytics"""
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    endpoint = Column(String, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    aez = Column(String)
    prediction_type = Column(String)
    result = Column(JSON)
    user_id = Column(String, nullable=True)

class LocationCache(Base):
    """Cache geocoding results"""
    __tablename__ = "location_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    aez = Column(String)
    cached_at = Column(DateTime, default=datetime.utcnow)

class RoadCache(Base):
    """Cache road data"""
    __tablename__ = "road_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    location_key = Column(String, unique=True, index=True)
    geojson_data = Column(JSON)
    cached_at = Column(DateTime, default=datetime.utcnow)

# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
