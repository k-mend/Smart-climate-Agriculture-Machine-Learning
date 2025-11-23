from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

# =============================================================================
# HEALTH CHECK
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


# =============================================================================
# LOCATION ANALYSIS
# =============================================================================

class LocationAnalysisRequest(BaseModel):
    location: str = Field(..., description="Location name (e.g., 'Nairobi, Kenya')")
    current_month: Optional[int] = Field(None, ge=1, le=12, description="Current month (1-12)")
    humanize: bool = Field(False, description="Return AI-humanized summary")


class MonthlyRainfallForecast(BaseModel):
    """Rainfall forecast for a single month"""
    month_name: str
    will_rain: bool
    amount_mm: float


class TemperatureRange(BaseModel):
    """Temperature range for a crop"""
    min: float
    max: float
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None


class RainfallRange(BaseModel):
    """Rainfall range for a crop"""
    min: float
    max: float
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None


class CropRecommendation(BaseModel):
    """A single crop recommendation"""
    crop_name: str
    scientific_name: str
    suitability_score: float
    temperature_range: TemperatureRange
    rainfall_range: RainfallRange


class Coordinates(BaseModel):
    """Latitude and longitude"""
    latitude: float
    longitude: float


class LocationAnalysisResponse(BaseModel):
    location: str
    coordinates: Coordinates
    aez: str
    best_planting_times: List[str]
    rainfall_forecast: Dict[str, MonthlyRainfallForecast]  # Changed from Dict[str, float]
    recommended_crops: List[CropRecommendation]
    average_annual_rainfall: float
    soil_type: Optional[str] = None
    humanized_summary: Optional[str] = None


# =============================================================================
# CROP ANALYSIS
# =============================================================================

class CropAnalysisRequest(BaseModel):
    crop_name: str = Field(..., description="Name of crop or herb")
    location: str = Field(..., description="Location name")
    humanize: bool = Field(False, description="Return AI-humanized summary")


class OptimalConditions(BaseModel):
    """Optimal growing conditions for a crop"""
    temperature_min: float
    temperature_max: float
    rainfall_min: float
    rainfall_max: float
    optimal_ph_min: Optional[float] = None
    optimal_ph_max: Optional[float] = None


class SuitabilityFactors(BaseModel):
    """Factors affecting crop suitability"""
    temperature: str
    rainfall: str
    aez: Optional[str] = None
    climate_zone: Optional[str] = None


class CropAnalysisResponse(BaseModel):
    crop_name: str
    scientific_name: str
    location: str
    coordinates: Coordinates
    optimal_conditions: OptimalConditions
    best_planting_time: str
    growth_duration_days: int
    suitability_score: float
    suitability_factors: SuitabilityFactors
    humanized_summary: Optional[str] = None


# =============================================================================
# SMART ROUTE
# =============================================================================

class SmartRouteRequest(BaseModel):
    start_point: str = Field(..., description="Starting location (farm)")
    end_point: str = Field(..., description="Destination location (market)")


class RouteAlternative(BaseModel):
    """An alternative route option"""
    distance_km: float
    estimated_time_minutes: float
    route_geometry: Dict[str, Any]


class SmartRouteResponse(BaseModel):
    start_point: str
    end_point: str
    start_coordinates: Coordinates
    end_coordinates: Coordinates
    route_geometry: Dict[str, Any]
    distance_km: float
    estimated_time_minutes: float
    rainfall_forecast: float
    vulnerable_roads_avoided: int
    weather_alert: bool
    alternative_routes: List[RouteAlternative] = []


# =============================================================================
# AGRIBRICKS AI ASSISTANT
# =============================================================================

class AgribricksAIRequest(BaseModel):
    question: str = Field(..., description="Farmer's question about agriculture")
    location: Optional[str] = Field(None, description="Optional location context")
    crop_type: Optional[str] = Field(None, description="Optional crop type context")
    language: Optional[str] = Field("en", description="Response language (en, sw, etc.)")


class AgribricksAIResponse(BaseModel):
    question: str
    answer: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    location_context: Optional[str] = None
    crop_context: Optional[str] = None


class CropDiseaseDetectionRequest(BaseModel):
    crop_type: Optional[str] = Field(None, description="Type of crop in the image")
    location: Optional[str] = Field(None, description="Location for regional disease context")
    additional_symptoms: Optional[str] = Field(None, description="Additional symptoms observed by farmer")
    # Note: image will be uploaded as multipart/form-data


class CropDiseaseDetectionResponse(BaseModel):
    diagnosis: str = Field(..., description="Primary disease diagnosis")
    confidence: str = Field(..., description="Confidence level: High, Medium, or Low")
    severity: str = Field(..., description="Disease severity: Mild, Moderate, or Severe")
    treatment_recommendations: List[str] = Field(default_factory=list, description="Immediate treatment steps")
    management_strategy: List[str] = Field(default_factory=list, description="Long-term management approach")
    crop_type: Optional[str] = None
    location: Optional[str] = None
    additional_symptoms: Optional[str] = None
    full_analysis: Optional[str] = Field(None, description="Complete diagnostic analysis")
    model_used: Optional[str] = Field(None, description="AI model used for analysis")


# =============================================================================
# DATABASE MODELS (for API responses)
# =============================================================================

class PredictionLogResponse(BaseModel):
    id: int
    timestamp: datetime
    endpoint: str
    location: str
    prediction_type: str
    result: Dict[str, Any]
    
    class Config:
        from_attributes = True
