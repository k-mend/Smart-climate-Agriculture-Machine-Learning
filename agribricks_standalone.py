#!/usr/bin/env python3
"""
Standalone Agribricks AI Assistant API
A simple FastAPI server with just the AI assistant endpoint
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the AI assistant
from app.agribricks_ai import AgribricksAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agribricks AI Assistant",
    description="AI-powered agricultural advice for farmers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
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

# Initialize AI assistant
agribricks_ai = AgribricksAI()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🌱 Agribricks AI Assistant - Expert Agricultural Advice",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "ai_assistant": "/api/agribricks-ai",
            "disease_detection": "/api/crop-disease-detection",
            "health_check": "/api/agribricks-ai/health",
            "examples": "/api/examples",
            "documentation": "/docs"
        }
    }

@app.post("/api/agribricks-ai", response_model=AgribricksAIResponse)
async def agribricks_ai_assistant(request: AgribricksAIRequest):
    """
    🤖 Agribricks AI Assistant - Get expert agricultural advice
    
    This endpoint provides intelligent, context-aware agricultural advice using
    advanced AI models. Perfect for farmers seeking guidance on:
    
    🌱 Crop selection and management
    🐛 Pest and disease control  
    🌿 Soil health and fertilization
    🌦️ Weather-based farming decisions
    ♻️ Sustainable farming practices
    💧 Irrigation and water management
    📦 Post-harvest handling and storage
    💰 Market timing and economics
    🌍 Climate-smart agriculture techniques
    
    Returns:
    - Expert agricultural advice
    - Actionable recommendations  
    - Confidence score
    - Relevant sources and tips
    """
    try:
        logger.info(f"🌾 Agribricks AI request: {request.question[:100]}...")
        
        # Get AI response
        ai_response = await agribricks_ai.get_agricultural_advice(
            question=request.question,
            location=request.location,
            crop_type=request.crop_type,
            language=request.language
        )
        
        # Check for errors in AI response
        if "error" in ai_response:
            logger.warning(f"⚠️ AI service error: {ai_response['error']}")
        
        # Prepare response
        response_data = AgribricksAIResponse(
            question=request.question,
            answer=ai_response["answer"],
            confidence_score=ai_response["confidence_score"],
            sources=ai_response["sources"],
            recommendations=ai_response["recommendations"],
            location_context=request.location,
            crop_context=request.crop_type
        )
        
        logger.info(f"✅ Response generated with confidence: {ai_response['confidence_score']:.2f}")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Error in Agribricks AI assistant: {str(e)}")
        
        # Return a helpful error response instead of raising HTTP exception
        return AgribricksAIResponse(
            question=request.question,
            answer=f"I apologize, but I'm currently experiencing technical difficulties. "
                   f"For immediate assistance, please contact your local agricultural extension office. "
                   f"Error details: {str(e)}",
            confidence_score=0.0,
            sources=["Local agricultural extension services", "Agricultural research institutions"],
            recommendations=[
                "Contact your local agricultural extension office",
                "Consult with experienced farmers in your area", 
                "Check government agricultural websites for your region"
            ],
            location_context=request.location,
            crop_context=request.crop_type
        )

@app.get("/api/agribricks-ai/health")
async def agribricks_ai_health():
    """🔍 Check Agribricks AI service health"""
    try:
        # Test if the AI service is working
        test_response = await agribricks_ai.get_agricultural_advice(
            question="What is sustainable agriculture?",
            location="Test Location",
            crop_type="General"
        )
        
        is_healthy = "error" not in test_response and len(test_response["answer"]) > 50
        groq_key_configured = bool(os.getenv("GROQ_API_KEY"))
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "message": "🌱 Agribricks AI is operational" if is_healthy else "⚠️ AI service experiencing issues",
            "service": "Agribricks AI Assistant",
            "model": "Groq Llama3-70B",
            "groq_api_configured": groq_key_configured,
            "capabilities": [
                "🌾 Crop management advice",
                "🐛 Pest and disease control",
                "🌿 Soil health guidance", 
                "🌦️ Weather-based decisions",
                "♻️ Sustainable farming practices",
                "💰 Market timing advice"
            ],
            "test_response_length": len(test_response["answer"]) if is_healthy else 0,
            "confidence_score": test_response.get("confidence_score", 0.0)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"❌ AI service error: {str(e)}",
            "service": "Agribricks AI Assistant",
            "groq_api_configured": bool(os.getenv("GROQ_API_KEY")),
            "error": str(e)
        }

@app.post("/api/crop-disease-detection", response_model=CropDiseaseDetectionResponse)
async def crop_disease_detection(
    image: UploadFile = File(..., description="Plant image for disease analysis"),
    crop_type: Optional[str] = Form(None, description="Type of crop in the image"),
    location: Optional[str] = Form(None, description="Location for regional disease context"),
    additional_symptoms: Optional[str] = Form(None, description="Additional symptoms observed")
):
    """
    🔬 Crop Disease Detection - AI-powered plant disease diagnosis from images
    
    Upload an image of your crop to get:
    - 🦠 Disease identification and diagnosis
    - 📊 Confidence level and severity assessment
    - 💊 Treatment recommendations (organic & chemical)
    - 🌱 Management strategies and prevention tips
    - 🌍 Regional disease context
    
    **Supported formats**: JPEG, PNG, GIF, WebP
    **Recommended**: Clear, well-lit photos of affected plant parts
    
    **AI Model**: Llama-3.2-90B Vision Preview for accurate plant pathology
    """
    try:
        logger.info(f"🔬 Disease detection request for {crop_type or 'unknown crop'}")
        
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file (JPEG, PNG, GIF, WebP)."
            )
        
        # Check file size (limit to 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        image_data = await image.read()
        
        if len(image_data) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Please upload an image smaller than 10MB."
            )
        
        if len(image_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty image file. Please upload a valid image."
            )
        
        # Get disease diagnosis from AI
        diagnosis_result = await agribricks_ai.detect_crop_disease(
            image_data=image_data,
            crop_type=crop_type,
            location=location,
            additional_symptoms=additional_symptoms
        )
        
        # Check for errors in diagnosis
        if "error" in diagnosis_result:
            logger.warning(f"Disease detection error: {diagnosis_result['error']}")
        
        # Prepare response
        response_data = CropDiseaseDetectionResponse(
            diagnosis=diagnosis_result["diagnosis"],
            confidence=diagnosis_result["confidence"],
            severity=diagnosis_result["severity"],
            treatment_recommendations=diagnosis_result["treatment_recommendations"],
            management_strategy=diagnosis_result["management_strategy"],
            crop_type=crop_type,
            location=location,
            additional_symptoms=additional_symptoms,
            full_analysis=diagnosis_result.get("full_analysis"),
            model_used=diagnosis_result.get("model_used")
        )
        
        logger.info(f"✅ Disease diagnosis completed: {diagnosis_result['diagnosis'][:50]}...")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in crop disease detection: {str(e)}")
        
        # Return helpful error response
        return CropDiseaseDetectionResponse(
            diagnosis=f"I encountered an error while analyzing your image: {str(e)}. Please try again with a clear, well-lit image of the affected plant.",
            confidence="Low",
            severity="Unknown",
            treatment_recommendations=[
                "Try uploading the image again",
                "Ensure the image is clear and well-lit",
                "Take photos of affected leaves, stems, or fruits",
                "Contact your local agricultural extension office"
            ],
            management_strategy=[
                "Monitor plants closely for symptom changes",
                "Isolate affected plants if possible",
                "Document symptoms with multiple photos",
                "Consult with experienced farmers in your area"
            ],
            crop_type=crop_type,
            location=location,
            additional_symptoms=additional_symptoms,
            full_analysis=f"Error occurred during analysis: {str(e)}",
            model_used="llama-3.2-90b-vision-preview"
        )

@app.get("/api/examples")
async def get_examples():
    """📚 Get example questions for the AI assistant"""
    return {
        "example_questions": [
            {
                "category": "🌾 Crop Management",
                "questions": [
                    "What are the best crops to plant during the rainy season in Kenya?",
                    "When should I harvest my maize crop?",
                    "How do I improve maize yield on my farm?"
                ]
            },
            {
                "category": "🐛 Pest Control", 
                "questions": [
                    "How do I control aphids on my tomato plants naturally?",
                    "What are the signs of fall armyworm in maize?",
                    "How can I prevent fungal diseases in my crops?"
                ]
            },
            {
                "category": "🌿 Soil Health",
                "questions": [
                    "How can I improve my soil fertility naturally?",
                    "What is the best organic fertilizer for vegetables?",
                    "How do I test my soil pH at home?"
                ]
            },
            {
                "category": "🌦️ Weather & Climate",
                "questions": [
                    "How should I prepare my farm for the dry season?",
                    "What crops are drought-resistant?",
                    "How does climate change affect farming in East Africa?"
                ]
            },
            {
                "category": "🔬 Disease Detection",
                "description": "Upload plant images for AI-powered disease diagnosis",
                "endpoint": "/api/crop-disease-detection",
                "examples": [
                    "Upload photo of yellowing tomato leaves",
                    "Analyze spots on maize leaves",
                    "Diagnose wilting in bean plants",
                    "Identify fungal infections on crops"
                ]
            }
        ],
        "usage_tips": [
            "Be specific about your location for better advice",
            "Mention the crop type you're working with",
            "Ask follow-up questions for more detailed guidance",
            "Include your current farming challenges in the question"
        ],
        "disease_detection_tips": [
            "📸 Take clear, well-lit photos of affected plant parts",
            "🔍 Focus on leaves, stems, fruits showing symptoms",
            "📏 Include close-up and wider shots for context",
            "🌅 Best lighting: natural daylight, avoid flash",
            "📝 Describe additional symptoms you observe",
            "📍 Mention your location for regional disease context"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Check if Groq API key is configured
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key in the .env file")
        print("You can get a free API key from: https://console.groq.com/")
    else:
        print("✅ GROQ_API_KEY configured")
    
    print("🚀 Starting Agribricks AI Assistant...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌱 Ready to help farmers with AI-powered advice!")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)