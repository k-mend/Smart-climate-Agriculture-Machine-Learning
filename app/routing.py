import openrouteservice as ors
import osmnx as ox
import geopandas as gpd
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional
import json

from .config import settings

logger = logging.getLogger(__name__)

class RoutingService:
    """Handles routing and road vulnerability analysis"""
    
    def __init__(self):
        self.ors_client = ors.Client(key=settings.ORS_API_KEY)
        self.road_cache_dir = Path(settings.ROAD_DATA_DIR)
        self.road_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_vulnerable_roads(
        self, 
        location_name: str, 
        lat: float, 
        lon: float
    ) -> List[Dict]:
        """
        Get vulnerable roads for a location
        
        Uses caching strategy:
        1. Check if geojson file exists for location
        2. If not, fetch from OSM and cache
        3. Return vulnerable road segments
        """
        try:
            # Create cache filename
            cache_filename = f"{location_name.lower().replace(' ', '_')}_vulnerable_roads.geojson"
            cache_path = self.road_cache_dir / cache_filename
            
            # Check cache
            if cache_path.exists() and settings.ENABLE_ROAD_CACHE:
                logger.info(f"Loading vulnerable roads from cache: {cache_filename}")
                with open(cache_path, 'r') as f:
                    geojson_data = json.load(f)
                return self._extract_road_segments(geojson_data)
            
            # Cache miss - fetch from OSM
            logger.info(f"Fetching vulnerable roads from OSM for: {location_name}")
            
            # Get road network for the area
            G = ox.graph_from_point(
                (lat, lon),
                dist=10000,  # 10km radius
                network_type='drive',
                simplify=True
            )
            
            # Convert to GeoDataFrame
            gdf_edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
            
            # Filter for vulnerable road types
            vulnerable_roads = gdf_edges[
                gdf_edges['highway'].isin(settings.VULNERABLE_ROAD_TYPES)
            ]
            
            if vulnerable_roads.empty:
                logger.warning(f"No vulnerable roads found for {location_name}")
                return []
            
            # Save to cache
            vulnerable_roads.to_file(cache_path, driver='GeoJSON')
            logger.info(f"Cached vulnerable roads to: {cache_filename}")
            
            # Convert to geojson dict
            geojson_data = json.loads(vulnerable_roads.to_json())
            
            return self._extract_road_segments(geojson_data)
            
        except Exception as e:
            logger.error(f"Error getting vulnerable roads: {str(e)}")
            return []
    
    def _extract_road_segments(self, geojson_data: Dict) -> List[Dict]:
        """Extract road segments from GeoJSON"""
        segments = []
        
        for feature in geojson_data.get('features', []):
            if feature['geometry']['type'] == 'LineString':
                segments.append({
                    'coordinates': feature['geometry']['coordinates'],
                    'road_type': feature['properties'].get('highway', 'unknown')
                })
        
        return segments
    
    def calculate_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        avoid_roads: List[Dict] = None
    ) -> Dict:
        """
        Calculate optimal route using OpenRouteService
        
        Args:
            start_coords: (lat, lon) tuple
            end_coords: (lat, lon) tuple
            avoid_roads: List of road segments to avoid
        
        Returns:
            Route information including geometry, distance, duration
        """
        try:
            # Convert coordinates to ORS format (lon, lat)
            start = [start_coords[1], start_coords[0]]
            end = [end_coords[1], end_coords[0]]
            
            # Build request parameters
            params = {
                'coordinates': [start, end],
                'profile': 'driving-car',
                'format': 'geojson',
                'instructions': True,
                'elevation': False
            }
            
            # Add avoid polygons if vulnerable roads exist
            if avoid_roads and len(avoid_roads) > 0:
                # Convert road segments to avoid polygons
                avoid_polygons = self._create_avoid_polygons(avoid_roads)
                if avoid_polygons:
                    params['options'] = {
                        'avoid_polygons': avoid_polygons
                    }
            
            # Request route
            route = self.ors_client.directions(**params)
            
            # Extract route information
            if route and 'features' in route and len(route['features']) > 0:
                feature = route['features'][0]
                properties = feature['properties']
                
                return {
                    'geometry': feature['geometry'],
                    'distance': properties['summary']['distance'] / 1000,  # Convert to km
                    'duration': properties['summary']['duration'] / 60,  # Convert to minutes
                    'segments': properties.get('segments', [])
                }
            else:
                raise Exception("No route found")
            
        except Exception as e:
            logger.error(f"Error calculating route: {str(e)}")
            # Return direct route as fallback
            return self._calculate_direct_route(start_coords, end_coords)
    
    def _create_avoid_polygons(self, road_segments: List[Dict]) -> Dict:
        """Create buffer polygons around vulnerable roads to avoid"""
        try:
            # Create buffer around road segments
            # Simplified implementation - in production use proper geometry
            polygons = []
            
            for segment in road_segments[:10]:  # Limit to 10 segments
                coords = segment['coordinates']
                if len(coords) >= 2:
                    # Create simple polygon (buffer would be better)
                    polygons.append({
                        'type': 'Polygon',
                        'coordinates': [coords]
                    })
            
            if polygons:
                return {
                    'type': 'FeatureCollection',
                    'features': [{
                        'type': 'Feature',
                        'geometry': poly
                    } for poly in polygons]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating avoid polygons: {str(e)}")
            return None
    
    def _calculate_direct_route(
        self, 
        start_coords: Tuple[float, float], 
        end_coords: Tuple[float, float]
    ) -> Dict:
        """Calculate simple direct route as fallback"""
        from math import radians, cos, sin, asin, sqrt
        
        # Haversine formula for distance
        lat1, lon1 = start_coords
        lat2, lon2 = end_coords
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        
        return {
            'geometry': {
                'type': 'LineString',
                'coordinates': [[lon1, lat1], [lon2, lat2]]
            },
            'distance': km,
            'duration': km / 60 * 60,  # Assuming 60 km/h
            'segments': []
        }
