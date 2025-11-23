"""
SQLAlchemy ORM Models for Database Tables

This file defines the database schema for:
- Prediction logs (analytics)
- Location cache (geocoding results)
- Road cache (OSM road data)
- Crop data (ecocrop database)
- Weather data (NASA POWER data)
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, 
    Boolean, Text, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


# =============================================================================
# PREDICTION LOGGING
# =============================================================================

class PredictionLog(Base):
    """
    Store all API prediction requests for analytics and debugging
    """
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Request info
    endpoint = Column(String(100), index=True)  # e.g., 'location-analysis', 'crop-analysis'
    request_id = Column(String(50), unique=True, index=True)
    
    # Location data
    location_name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    aez = Column(String(100), index=True)
    
    # Prediction details
    prediction_type = Column(String(50))  # 'rainfall', 'crop', 'route'
    input_params = Column(JSON)  # Store request parameters
    result = Column(JSON)  # Store prediction results
    
    # Performance metrics
    processing_time_ms = Column(Float)
    model_version = Column(String(50))
    
    # User tracking (optional)
    user_id = Column(String(100), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_prediction_logs_timestamp_endpoint', 'timestamp', 'endpoint'),
        Index('ix_prediction_logs_aez_type', 'aez', 'prediction_type'),
    )


# =============================================================================
# CACHING TABLES
# =============================================================================

class LocationCache(Base):
    """
    Cache geocoding results to reduce external API calls
    """
    __tablename__ = "location_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location identifier
    location_name = Column(String(255), unique=True, index=True)
    location_name_normalized = Column(String(255), index=True)  # Lowercase, trimmed
    
    # Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Derived data
    aez = Column(String(100))
    county = Column(String(100))
    country = Column(String(100), default='Kenya')
    
    # Cache metadata
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # Data source
    source = Column(String(50), default='nominatim')  # nominatim, google, ors


class RoadCache(Base):
    """
    Cache road network data from OpenStreetMap
    """
    __tablename__ = "road_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location identifier
    location_key = Column(String(255), unique=True, index=True)  # e.g., 'meru_kenya'
    location_name = Column(String(255))
    
    # Bounding box
    min_lat = Column(Float)
    max_lat = Column(Float)
    min_lon = Column(Float)
    max_lon = Column(Float)
    
    # Road data
    geojson_data = Column(JSON)  # Full GeoJSON of vulnerable roads
    road_count = Column(Integer)
    total_length_km = Column(Float)
    
    # Cache metadata
    cached_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    file_path = Column(String(500))  # Path to .geojson file if stored on disk
    
    # Status
    is_valid = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


# =============================================================================
# CROP DATA
# =============================================================================

class Crop(Base):
    """
    Store crop information from Ecocrop database
    """
    __tablename__ = "crops"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    common_name = Column(String(255), index=True)
    scientific_name = Column(String(255), index=True)
    category = Column(String(100))  # CAT field
    
    # Temperature requirements (°C) - lowercase column names
    temp_min = Column(Float)  # tmin - absolute minimum
    temp_max = Column(Float)  # tmax - absolute maximum
    temp_opt_min = Column(Float)  # topmn - optimal minimum
    temp_opt_max = Column(Float)  # topmx - optimal maximum
    
    # Rainfall requirements (mm/year) - lowercase column names
    rainfall_min = Column(Float)  # rmin
    rainfall_max = Column(Float)  # rmax
    rainfall_opt_min = Column(Float)  # ropmn
    rainfall_opt_max = Column(Float)  # ropmx
    
    # Soil requirements - lowercase column names
    ph_min = Column(Float)  # phopmn
    ph_max = Column(Float)  # phopmx
    fertility = Column(String(50))  # fer
    salinity = Column(String(50))  # sal
    drainage = Column(String(50))  # dra
    
    # Growth duration (days) - lowercase column names
    growth_days_min = Column(Integer)  # gmin
    growth_days_max = Column(Integer)  # gmax
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    suitability_records = relationship("CropSuitability", back_populates="crop")


class CropSuitability(Base):
    """
    Pre-computed crop suitability for each AEZ
    """
    __tablename__ = "crop_suitability"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    crop_id = Column(Integer, ForeignKey('crops.id'), index=True)
    
    # Location
    aez = Column(String(100), index=True)
    
    # Suitability scores
    suitability_class = Column(Integer)  # 0=Not suitable, 1=Marginal, 2=Highly suitable
    suitability_score = Column(Float)  # 0.0 to 1.0
    
    # Factor scores
    temperature_score = Column(Float)
    rainfall_score = Column(Float)
    
    # Recommendations
    best_planting_months = Column(String(100))  # e.g., "March,April,October"
    notes = Column(Text)
    
    # Metadata
    computed_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50))
    
    # Relationships
    crop = relationship("Crop", back_populates="suitability_records")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('crop_id', 'aez', name='uq_crop_aez'),
        Index('ix_crop_suitability_aez_score', 'aez', 'suitability_score'),
    )


# =============================================================================
# WEATHER DATA
# =============================================================================

class WeatherRecord(Base):
    """
    Store historical weather data from NASA POWER
    """
    __tablename__ = "weather_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location
    aez = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Date
    date = Column(DateTime, index=True)
    year = Column(Integer, index=True)
    month = Column(Integer, index=True)
    day = Column(Integer)
    
    # Weather variables - lowercase column names
    precipitation = Column(Float)  # prectotcorr (mm)
    temperature = Column(Float)  # t2m (°C)
    humidity = Column(Float)  # rh2m (%)
    solar_radiation = Column(Float)  # allsky_sfc_sw_dwn (MJ/m²/day)
    
    # Metadata
    data_source = Column(String(50), default='nasa_power')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('ix_weather_aez_date', 'aez', 'date'),
        Index('ix_weather_year_month', 'year', 'month'),
        UniqueConstraint('aez', 'date', name='uq_weather_aez_date'),
    )


class WeatherSummary(Base):
    """
    Pre-aggregated weather statistics by AEZ
    """
    __tablename__ = "weather_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location
    aez = Column(String(100), unique=True, index=True)
    
    # Annual statistics
    avg_annual_rainfall = Column(Float)
    rainfall_std = Column(Float)
    min_annual_rainfall = Column(Float)
    max_annual_rainfall = Column(Float)
    
    avg_temperature = Column(Float)
    temperature_std = Column(Float)
    min_temperature = Column(Float)
    max_temperature = Column(Float)
    
    avg_humidity = Column(Float)
    humidity_std = Column(Float)
    
    avg_solar_radiation = Column(Float)
    solar_radiation_std = Column(Float)
    
    # Seasonal patterns (JSON with monthly averages)
    monthly_rainfall = Column(JSON)  # {"1": 45.2, "2": 38.1, ...}
    monthly_temperature = Column(JSON)
    
    # Rainy seasons
    long_rains_start = Column(Integer)  # Month number
    long_rains_end = Column(Integer)
    short_rains_start = Column(Integer)
    short_rains_end = Column(Integer)
    
    # Metadata
    years_of_data = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)


# =============================================================================
# ROUTING DATA
# =============================================================================

class RouteLog(Base):
    """
    Log routing requests and results
    """
    __tablename__ = "route_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Start point
    start_name = Column(String(255))
    start_lat = Column(Float)
    start_lon = Column(Float)
    start_aez = Column(String(100))
    
    # End point
    end_name = Column(String(255))
    end_lat = Column(Float)
    end_lon = Column(Float)
    
    # Route details
    distance_km = Column(Float)
    duration_minutes = Column(Float)
    
    # Weather conditions
    rainfall_forecast_mm = Column(Float)
    weather_alert = Column(Boolean, default=False)
    
    # Road avoidance
    vulnerable_roads_count = Column(Integer, default=0)
    roads_avoided = Column(Boolean, default=False)
    
    # User tracking
    user_id = Column(String(100), nullable=True, index=True)


# =============================================================================
# USER FEEDBACK (Optional)
# =============================================================================

class UserFeedback(Base):
    """
    Store user feedback on predictions for model improvement
    """
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Link to prediction
    prediction_log_id = Column(Integer, ForeignKey('prediction_logs.id'), nullable=True)
    
    # Feedback
    rating = Column(Integer)  # 1-5 stars
    was_accurate = Column(Boolean)
    comments = Column(Text)
    
    # Context
    endpoint = Column(String(100))
    location = Column(String(255))
    
    # User
    user_id = Column(String(100), nullable=True)
