from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # API Keys
    ORS_API_KEY: str
    OPENROUTER_API_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/climate_agri_db"
    
    # Model paths
    MODELS_DIR: str = "./models"
    DATA_DIR: str = "./data"
    ROAD_DATA_DIR: str = "./data/road_data"
    
    # Model file extension (using joblib for compression)
    MODEL_FILE_EXT: str = ".joblib"
    
    # Rainfall threshold for road vulnerability (mm)
    RAINFALL_THRESHOLD: float = 20.0
    
    # OpenRouteService settings
    ORS_BASE_URL: str = "https://api.openrouteservice.org"
    ORS_TIMEOUT: int = 30
    
    # AI Humanizer settings
    OPENROUTER_MODEL: str = "anthropic/claude-3-haiku"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Cache settings
    ENABLE_ROAD_CACHE: bool = True
    CACHE_EXPIRY_HOURS: int = 24
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # Application
    APP_NAME: str = "Climate-Smart Agriculture API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # AEZ mapping - Kenya's agro-ecological zones
    AEZ_ZONES: dict = {
        "Highlands (Humid)": {"temp_range": (10, 20), "rainfall_range": (1200, 2000)},
        "Upper Midlands (High Potential)": {"temp_range": (18, 25), "rainfall_range": (1000, 1600)},
        "Lower Midlands (Semi-Arid)": {"temp_range": (22, 30), "rainfall_range": (500, 900)},
        "Coastal Lowlands (Humid)": {"temp_range": (24, 32), "rainfall_range": (900, 1400)},
        "Arid Lowlands (Arid)": {"temp_range": (26, 35), "rainfall_range": (200, 500)}
    }
    
    # Vulnerable road types (OSM tags)
    VULNERABLE_ROAD_TYPES: list = [
        'track',
        'unclassified', 
        'path',
        'footway',
        'service'
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
