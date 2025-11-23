import httpx
import logging
from typing import Dict, Any

from .config import settings
from .schemas import LocationAnalysisResponse, CropAnalysisResponse

logger = logging.getLogger(__name__)

class AIHumanizer:
    """Uses OpenRouter API to humanize ML predictions"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _call_openrouter(self, prompt: str) -> str:
        """Make API call to OpenRouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful agricultural advisor. Convert technical data into friendly, actionable advice for farmers. Be warm, encouraging, and practical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            return "Unable to generate humanized summary at this time."
    
    async def humanize_location_analysis(
        self, 
        data: LocationAnalysisResponse
    ) -> str:
        """Convert location analysis to friendly advice"""
        
        crops_list = ", ".join([c.crop_name for c in data.recommended_crops[:3]])
        planting_times = ", ".join(data.best_planting_times)
        
        prompt = f"""
        Create a friendly summary for a farmer about their location: {data.location}
        
        Key information:
        - Location is in {data.aez} zone
        - Best times to plant: {planting_times}
        - Average annual rainfall: {data.average_annual_rainfall:.0f}mm
        - Top recommended crops: {crops_list}
        - Soil type: {data.soil_type}
        
        Write 2-3 sentences giving practical planting advice. Be encouraging and specific.
        """
        
        return await self._call_openrouter(prompt)
    
    async def humanize_crop_analysis(
        self, 
        data: CropAnalysisResponse
    ) -> str:
        """Convert crop analysis to friendly advice"""
        
        prompt = f"""
        Create a friendly summary for a farmer wanting to grow {data.crop_name} at {data.location}
        
        Key information:
        - Suitability score: {data.suitability_score:.2f} (0-1 scale)
        - Best planting time: {data.best_planting_time}
        - Growth duration: {data.growth_duration_days} days
        - Temperature needs: {data.optimal_conditions['temperature_min']}°C - {data.optimal_conditions['temperature_max']}°C
        - Rainfall needs: {data.optimal_conditions['rainfall_min']}mm - {data.optimal_conditions['rainfall_max']}mm
        
        Write 2-3 sentences with practical advice about growing this crop. Be encouraging if suitable, honest if challenging.
        """
        
        return await self._call_openrouter(prompt)
    
    def __del__(self):
        """Cleanup async client"""
        try:
            import asyncio
            asyncio.create_task(self.client.aclose())
        except:
            pass
