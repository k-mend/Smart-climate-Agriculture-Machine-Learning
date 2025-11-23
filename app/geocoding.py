from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging
from typing import Dict, Optional, Tuple

from .config import settings

logger = logging.getLogger(__name__)

class GeocodingService:
    """Handles geocoding and reverse geocoding"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="climate_agri_app")
        
        # AEZ boundaries for Kenya (simplified - in production use actual shapefiles)
        # Zones: Highlands (Humid), Upper Midlands (High Potential), 
        #        Lower Midlands (Semi-Arid), Coastal Lowlands (Humid), 
        #        Arid Lowlands (Arid)
        self.aez_boundaries = {
            "Highlands (Humid)": {
                "lat_range": (-1.5, 1.0),
                "lon_range": (34.0, 38.0),
                "altitude_min": 1800
            },
            "Upper Midlands (High Potential)": {
                "lat_range": (-1.0, 1.5),
                "lon_range": (34.5, 38.5),
                "altitude_min": 1200,
                "altitude_max": 1800
            },
            "Lower Midlands (Semi-Arid)": {
                "lat_range": (-3.0, 2.0),
                "lon_range": (35.0, 40.0),
                "altitude_min": 600,
                "altitude_max": 1200
            },
            "Coastal Lowlands (Humid)": {
                "lat_range": (-5.0, -1.0),
                "lon_range": (39.0, 41.5),
                "altitude_max": 500
            },
            "Arid Lowlands (Arid)": {
                "lat_range": (-2.0, 4.5),
                "lon_range": (35.0, 41.0),
                "altitude_max": 900
            }
        }
    
    def geocode_location(self, location_name: str) -> Optional[Dict[str, float]]:
        """
        Convert location name to coordinates
        
        Args:
            location_name: Name of location (e.g., "Nairobi, Kenya")
        
        Returns:
            Dictionary with lat and lon, or None if not found
        """
        try:
            location = self.geolocator.geocode(location_name, timeout=10)
            
            if location:
                return {
                    "lat": location.latitude,
                    "lon": location.longitude
                }
            else:
                logger.warning(f"Location not found: {location_name}")
                return None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding error for {location_name}: {str(e)}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to location name
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Location name string or None
        """
        try:
            location = self.geolocator.reverse(
                f"{lat}, {lon}", 
                timeout=10,
                language='en'
            )
            
            if location:
                # Extract city or town name
                address = location.raw.get('address', {})
                
                # Try to get the most specific location
                for key in ['city', 'town', 'village', 'county', 'state']:
                    if key in address:
                        return f"{address[key]}, Kenya"
                
                return location.address
            
            return None
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Reverse geocoding error: {str(e)}")
            return None
    
    def get_aez_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Determine Agro-Ecological Zone from coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            AEZ name or None
        """
        # Check each AEZ boundary
        for aez_name, boundaries in self.aez_boundaries.items():
            lat_in_range = (
                boundaries['lat_range'][0] <= lat <= boundaries['lat_range'][1]
            )
            lon_in_range = (
                boundaries['lon_range'][0] <= lon <= boundaries['lon_range'][1]
            )
            
            if lat_in_range and lon_in_range:
                return aez_name
        
        # Default to closest match based on location heuristics
        logger.warning(f"No exact AEZ match for ({lat}, {lon}), using heuristics")
        
        # Simple heuristic based on latitude and longitude for Kenya
        if lat > 0:
            # Northern Kenya - mostly arid
            if lon > 38:
                return "Arid Lowlands (Arid)"
            else:
                return "Upper Midlands (High Potential)"
        elif lat < -3:
            # Southern coastal region
            if lon > 39:
                return "Coastal Lowlands (Humid)"
            else:
                return "Lower Midlands (Semi-Arid)"
        else:
            # Central Kenya
            if lon < 37:
                return "Highlands (Humid)"
            elif lon > 39:
                return "Coastal Lowlands (Humid)"
            else:
                return "Upper Midlands (High Potential)"
    
    def get_soil_type(self, lat: float, lon: float) -> Optional[str]:
        """
        Get soil type for coordinates
        
        Note: This is a placeholder. In production, integrate with:
        - SoilGrids API
        - National soil databases
        - FAO soil maps
        """
        # Simplified mapping based on AEZ for Kenya
        aez = self.get_aez_from_coordinates(lat, lon)
        
        soil_mapping = {
            "Highlands (Humid)": "Humic Nitisols (deep, well-drained volcanic soils)",
            "Upper Midlands (High Potential)": "Rhodic Ferralsols (red, well-weathered soils)",
            "Lower Midlands (Semi-Arid)": "Chromic Luvisols (clay-rich, moderately fertile)",
            "Coastal Lowlands (Humid)": "Ferralic Arenosols (sandy, well-drained coastal soils)",
            "Arid Lowlands (Arid)": "Calcic Vertisols (dark, cracking clay soils)"
        }
        
        return soil_mapping.get(aez, "Unknown")
    
    def calculate_distance(
        self, 
        coord1: Tuple[float, float], 
        coord2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two coordinates in km
        
        Args:
            coord1: (lat, lon) tuple
            coord2: (lat, lon) tuple
        
        Returns:
            Distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Haversine formula
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        
        return km
