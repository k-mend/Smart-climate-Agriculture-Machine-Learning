from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import List

from .config import settings
from .database import get_db, engine, Base
from .schemas import (
    LocationAnalysisRequest, LocationAnalysisResponse,
    CropAnalysisRequest, CropAnalysisResponse,
    SmartRouteRequest, SmartRouteResponse,
    HealthResponse, Coordinates, CropRecommendation,
    TemperatureRange, RainfallRange, MonthlyRainfallForecast,
    OptimalConditions, SuitabilityFactors
)
from .ml_models import MLModels
from .routing import RoutingService
from .geocoding import GeocodingService
from .ai_humanizer import AIHumanizer

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Climate-Smart Agriculture & Smart Mobility API",
    description="ML-powered API for agricultural insights and smart routing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ml_models = MLModels()
routing_service = RoutingService()
geocoding_service = GeocodingService()
ai_humanizer = AIHumanizer()

@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    logger.info("Loading ML models...")
    ml_models.load_models()
    logger.info("ML models loaded successfully!")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        message="Climate-Smart Agriculture & Smart Mobility API is running",
        version="1.0.0"
    )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    models_loaded = ml_models.models_loaded
    return HealthResponse(
        status="healthy" if models_loaded else "degraded",
        message="All systems operational" if models_loaded else "Models not loaded",
        version="1.0.0"
    )

@app.post("/api/location-analysis", response_model=LocationAnalysisResponse)
async def location_analysis(
    request: LocationAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a location for agricultural insights
    
    Returns:
    - Best planting times
    - Rainfall predictions
    - Recommended crops
    - Average rainfall
    - Soil type (if available)
    """
    try:
        logger.info(f"Location analysis request for: {request.location}")
        
        # Get coordinates from location name
        coordinates = geocoding_service.geocode_location(request.location)
        if not coordinates:
            raise HTTPException(status_code=404, detail="Location not found")
        
        lat, lon = coordinates['lat'], coordinates['lon']
        
        # Determine AEZ (Agro-Ecological Zone) from coordinates
        aez = geocoding_service.get_aez_from_coordinates(lat, lon)
        if not aez:
            raise HTTPException(status_code=404, detail="Could not determine AEZ for location")
        
        # Get weather predictions
        rainfall_predictions = ml_models.predict_rainfall(
            aez=aez,
            current_month=request.current_month or datetime.now().month
        )
        
        # Determine best planting times (months with optimal rainfall starting)
        planting_times = ml_models.predict_planting_times(rainfall_predictions)
        
        # Get crop recommendations
        crop_recommendations_raw = ml_models.recommend_crops(
            aez=aez,
            temperature=rainfall_predictions['avg_temperature'],
            rainfall=rainfall_predictions['avg_annual_rainfall']
        )
        
        # Convert to proper schema format
        crop_recommendations = [
            CropRecommendation(
                crop_name=crop['crop_name'],
                scientific_name=crop['scientific_name'],
                suitability_score=crop['suitability_score'],
                temperature_range=TemperatureRange(
                    min=crop['temperature_range']['min'],
                    max=crop['temperature_range']['max'],
                    optimal_min=crop['temperature_range'].get('optimal_min'),
                    optimal_max=crop['temperature_range'].get('optimal_max')
                ),
                rainfall_range=RainfallRange(
                    min=crop['rainfall_range']['min'],
                    max=crop['rainfall_range']['max'],
                    optimal_min=crop['rainfall_range'].get('optimal_min'),
                    optimal_max=crop['rainfall_range'].get('optimal_max')
                )
            )
            for crop in crop_recommendations_raw[:5]  # Top 5 crops
        ]
        
        # Convert rainfall forecast to proper schema format
        rainfall_forecast = {
            key: MonthlyRainfallForecast(
                month_name=value['month_name'],
                will_rain=value['will_rain'],
                amount_mm=value['amount_mm']
            )
            for key, value in rainfall_predictions['monthly_forecast'].items()
        }
        
        # Calculate average rainfall
        avg_rainfall = rainfall_predictions['avg_annual_rainfall']
        
        # Get soil type (placeholder - requires soil database)
        soil_type = geocoding_service.get_soil_type(lat, lon)
        
        # Prepare response
        response_data = LocationAnalysisResponse(
            location=request.location,
            coordinates=Coordinates(latitude=lat, longitude=lon),
            aez=aez,
            best_planting_times=planting_times,
            rainfall_forecast=rainfall_forecast,
            recommended_crops=crop_recommendations,
            average_annual_rainfall=avg_rainfall,
            soil_type=soil_type
        )
        
        # Humanize response if requested
        if request.humanize:
            try:
                response_data.humanized_summary = await ai_humanizer.humanize_location_analysis(response_data)
            except Exception as e:
                logger.warning(f"Failed to humanize response: {e}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in location analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crop-analysis", response_model=CropAnalysisResponse)
async def crop_analysis(
    request: CropAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a specific crop for a given location
    
    Returns:
    - Optimal climatic conditions
    - Best planting time
    - Growth duration
    - Suitability score
    """
    try:
        logger.info(f"Crop analysis request: {request.crop_name} at {request.location}")
        
        # Get coordinates
        coordinates = geocoding_service.geocode_location(request.location)
        if not coordinates:
            raise HTTPException(status_code=404, detail="Location not found")
        
        lat, lon = coordinates['lat'], coordinates['lon']
        aez = geocoding_service.get_aez_from_coordinates(lat, lon)
        
        # Get crop information
        crop_info = ml_models.get_crop_info(request.crop_name)
        if not crop_info:
            raise HTTPException(status_code=404, detail=f"Crop '{request.crop_name}' not found in database")
        
        # Calculate suitability
        suitability = ml_models.calculate_crop_suitability(
            crop_name=request.crop_name,
            aez=aez,
            lat=lat,
            lon=lon
        )
        
        # Get best planting time for this specific crop
        best_planting_month = ml_models.get_best_planting_time_for_crop(
            crop_info=crop_info,
            aez=aez
        )
        
        response_data = CropAnalysisResponse(
            crop_name=request.crop_name,
            scientific_name=crop_info.get('scientific_name', 'N/A'),
            location=request.location,
            coordinates=Coordinates(latitude=lat, longitude=lon),
            optimal_conditions=OptimalConditions(
                temperature_min=crop_info['temp_min'],
                temperature_max=crop_info['temp_max'],
                rainfall_min=crop_info['rainfall_min'],
                rainfall_max=crop_info['rainfall_max'],
                optimal_ph_min=crop_info.get('ph_min', 5.5),
                optimal_ph_max=crop_info.get('ph_max', 7.5)
            ),
            best_planting_time=best_planting_month,
            growth_duration_days=crop_info.get('growth_duration', 90),
            suitability_score=suitability['score'],
            suitability_factors=SuitabilityFactors(
                temperature=suitability['factors'].get('temperature', 'Unknown'),
                rainfall=suitability['factors'].get('rainfall', 'Unknown'),
                aez=suitability['factors'].get('aez'),
                climate_zone=suitability['factors'].get('climate_zone')
            )
        )
        
        # Humanize response
        if request.humanize:
            try:
                response_data.humanized_summary = await ai_humanizer.humanize_crop_analysis(response_data)
            except Exception as e:
                logger.warning(f"Failed to humanize response: {e}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in crop analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/smart-route", response_model=SmartRouteResponse)
async def smart_route(
    request: SmartRouteRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate optimal route avoiding vulnerable roads during rainfall
    
    Returns:
    - Optimized route
    - Vulnerable roads to avoid
    - Estimated travel time
    - Weather forecast for route
    """
    try:
        logger.info(f"Smart route request from {request.start_point} to {request.end_point}")
        
        # Geocode start and end points
        start_coords = geocoding_service.geocode_location(request.start_point)
        end_coords = geocoding_service.geocode_location(request.end_point)
        
        if not start_coords or not end_coords:
            raise HTTPException(status_code=404, detail="Could not geocode one or both locations")
        
        # Get AEZ for start point
        aez = geocoding_service.get_aez_from_coordinates(
            start_coords['lat'], 
            start_coords['lon']
        )
        
        # Predict rainfall
        rainfall_forecast = ml_models.predict_rainfall(aez=aez)
        
        # Determine if heavy rain is expected
        heavy_rain_expected = rainfall_forecast['next_7days_total'] > settings.RAINFALL_THRESHOLD
        
        vulnerable_roads = []
        if heavy_rain_expected:
            # Get location name for road data
            location_name = geocoding_service.reverse_geocode(
                start_coords['lat'], 
                start_coords['lon']
            )
            
            # Get vulnerable roads
            vulnerable_roads = routing_service.get_vulnerable_roads(
                location_name=location_name,
                lat=start_coords['lat'],
                lon=start_coords['lon']
            )
        
        # Calculate route
        route = routing_service.calculate_route(
            start_coords=(start_coords['lat'], start_coords['lon']),
            end_coords=(end_coords['lat'], end_coords['lon']),
            avoid_roads=vulnerable_roads if heavy_rain_expected else []
        )
        
        response_data = SmartRouteResponse(
            start_point=request.start_point,
            end_point=request.end_point,
            start_coordinates=Coordinates(latitude=start_coords['lat'], longitude=start_coords['lon']),
            end_coordinates=Coordinates(latitude=end_coords['lat'], longitude=end_coords['lon']),
            route_geometry=route['geometry'],
            distance_km=route['distance'],
            estimated_time_minutes=route['duration'],
            rainfall_forecast=rainfall_forecast['next_7days_total'],
            vulnerable_roads_avoided=len(vulnerable_roads),
            weather_alert=heavy_rain_expected,
            alternative_routes=route.get('alternatives', [])
        )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart route: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
