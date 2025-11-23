# Climate-Smart Agriculture & Smart Mobility API
An ML-powered FastAPI backend for agricultural insights and intelligent routing based on weather predictions and road conditions.

# Crop and Rain Prediction API

This project provides a **FastAPI-based API** to predict the probability of rain, estimate precipitation amount, and recommend crops suitable for given weather conditions. The project was originally developed in Jupyter notebooks, and the final trained models are packaged for deployment.

## Problem Statement

This project uses **historical weather and crop data to build predictive models** that forecast rainfall (both probability and amount) and recommend suitable crops based on agro-climatic conditions. It addresses the challenge of agricultural planning under uncertain weather by combining **XGBoost and RandomForest models** for rain prediction with a crop recommendation system based on temperature and rainfall tolerances. The goal is to provide a **reliable, data-driven decision support tool for farmers**. The models and data are based on **Kenya's weather dataset**.


## Dataset

### NASA POWER API
Base URL: `https://power.larc.nasa.gov/api/temporal/daily/point`

#### Parameters
```python
# Historical date range for training
START_DATE = "19930101"
END_DATE = "20251031"

# Weather parameters from NASA POWER
# PRECTOTCORR - Precipitation (mm/day)
# T2M - Temperature at 2m (°C)
# RH2M - Relative Humidity at 2m (%)
# ALLSKY_SFC_SW_DWN - All Sky Surface Shortwave Downward Irradiance (W/m²) - proxy for sunshine
PARAMETERS = ["PRECTOTCORR", "T2M", "RH2M", "ALLSKY_SFC_SW_DWN"]
```

#### Locations
```python
LOCATIONS = {
    "highlands_humid_nyeri": {"name": "Nyeri (Highlands, Humid)", "latitude": -0.4167, "longitude": 36.9500},
    "upper_midlands_kitale": {"name": "Kitale (Upper Midlands, High Potential)", "latitude": 1.0167, "longitude": 35.0000},
    "lower_midlands_semiarid_machakos": {"name": "Machakos (Lower Midlands, Semi-Arid)", "latitude": -1.5167, "longitude": 37.2667},
    "coastal_lowlands_malindi": {"name": "Malindi (Coastal Lowlands, Humid)", "latitude": -3.2236, "longitude": 40.1300},
    "arid_lowlands_lodwar": {"name": "Lodwar (Arid Lowlands, Arid)", "latitude": 3.1191, "longitude": 35.5973}
}
```

### Ecocrop Dataset

You can download the Ecocrop dataset from their GitHub repo: [EcoCrop_DB.csv](https://github.com/OpenCLIM/ecocrop/blob/main/EcoCrop_DB.csv)


## Features

### 🌾 Agricultural Intelligence
- **Location Analysis**: Get agricultural insights for any location
  - Best planting times based on rainfall predictions
  - Recommended crops for your climate zone
  - Average rainfall data
  - Soil type information(if avaliable)

- **Crop Analysis**: Detailed analysis for specific crops
  - Optimal growing conditions
  - Best planting times
  - Growth duration
  - Suitability scoring

- **🤖 Agribricks AI Assistant**: Expert agricultural advice powered by AI
  - Context-aware farming guidance using Groq and LangChain
  - Crop management and pest control advice
  - Soil health and fertilization recommendations
  - Weather-based farming decisions
  - Sustainable farming practices
  - Multi-language support

- **🔬 Crop Disease Detection**: AI-powered plant pathology (NEW!)
  - Upload plant images for instant disease diagnosis
  - Uses Llama-4 Scout model for accurate image analysis
  - Provides treatment recommendations and management strategies
  - Supports multiple image formats (JPEG, PNG, GIF, WebP)
  - Regional disease context and severity assessment

###  Smart Mobility
- **Weather-Aware Routing**: Intelligent route planning
  - Avoids vulnerable roads during heavy rainfall
  - Real-time weather integration
  - Alternative route suggestions(if rainfall amount is above the threshold)
  - Distance and time estimates

## Tech Stack

- **Framework**: FastAPI
- **ML Models**: Scikit-learn, XGBoost, Random Forest
- **Database**: PostgreSQL
- **Containerization**: Docker, Pipenv
- **Routing**: OpenRouteService, OSMnx
- **Geocoding**: GeoPy
- **AI Enhancement**: OpenRouter (Claude), Groq (Llama3-70B)
- **AI Framework**: LangChain

## Project Structure

```
climate-agri-mobility/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── schemas.py           # Pydantic models
│   ├── database.py          # Database config
│   ├── ml_models.py         # ML inference
│   ├── routing.py           # Routing service
│   ├── geocoding.py         # Location services
│   ├── ai_humanizer.py      # AI response enhancement
│   └── agribricks_ai.py     # Agribricks AI Assistant
├── notebooks/
│   ├── 01_rainfall_prediction.ipynb
│   └── 02_crop_recommendation.ipynb
├── models/                  # Trained models (pkl files)
├── data/
│   ├── cleaned_ecocrop.csv
│   ├── merged_aez_weather.csv
│   └── road_data/          # Cached road networks
├── .env
├── Dockerfile
├── docker-compose.yml
├── Pipfile
└── README.md
```

## Installation

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL (or use Docker)
- API Keys:
  - OpenRouteService API key
  - OpenRouter API key (optional, for AI humanization)
  - Groq API key (for Agribricks AI Assistant)

### Setup

1. **Clone the repository**
```bash
git clone <git@github.com:k-mend/Smart-climate-Agriculture-Machine-Learning.git>
cd Smart-climate-Agriculture-Machine-Learning
```

2. **Create and configure .env file**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install dependencies with Pipenv**
```bash
python -m venv venv
source venv/bin/activate(linux)
pip install -r requirements.txt
```

4. **Or use Docker Compose (recommended)**
```bash
docker compose up -d
```
![Docker Build](Screenshots/Docker%20build.png)

## Training Models

### Step 1: Prepare Your Data
Place your datasets in the `data/` directory:
- `cleaned_ecocrop.csv` - Crop database (lowercase columns)
- `merged_aez_weather.csv` - Weather data with AEZ zones (lowercase columns)

### Step 2: Train Models
```bash
# Activate virtual environment
source venv/bin/activate

# Run notebooks in order
jupyter notebook notebooks/01_rainfall_prediction.ipynb
jupyter notebook notebooks/02_crop_recommendation.ipynb
```

The notebooks will:
1. Load and preprocess data
2. Train multiple models (Logistic Regression, Random Forest, XGBoost)
3. Evaluate using K-Fold cross-validation
4. Calculate AUC and RMSE scores
5. Save trained models to `models/` directory

### Step 3: Verify Models
Check that these files exist in `models/`:
- `rainfall_classifier.joblib` (compressed with joblib compress=5)
- `rainfall_regressor.joblib`
- `crop_recommendation_model.joblib`
- `scaler_rainfall.joblib`
- `scaler_crop.joblib`
- `aez_label_encoder.joblib`
- `aez_onehot_encoder.joblib`
- Various other encoder files

**Note**: We use `joblib` with `compress=5` instead of pickle because:
- Models can exceed 400MB with pickle, making deployment difficult
- Compressed models are typically 10-50MB, suitable for Render deployment
- Joblib handles numpy arrays more efficiently than pickle

## Running the API

### Using Docker (Recommended)
```bash
# Start all services
docker compose up -d
![Docker Build](Screenshots/Docker%20build.png)

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

### Running Locally
```bash
# Activate virtual environment if not already activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run the FastAPI application (includes all endpoints)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
![Running Locally](Screenshots/Running%20locally.png)


The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. Location Analysis
```bash
POST /api/location-analysis
```

**Request:**
```json
{
  "location": "Nairobi, Kenya",
  "current_month": 11,
  "humanize": true
}
```

**Response:**
```json
{
  "location": "Nairobi, Kenya",
  "coordinates": {"latitude": -1.286389, "longitude": 36.817223},
  "aez": "Highlands Semi-Humid",
  "best_planting_times": ["March", "October"],
  "rainfall_forecast": {
    "month_1": {"will_rain": true, "amount_mm": 45.2},
    ...
  },
  "recommended_crops": [
    {
      "crop_name": "Maize",
      "scientific_name": "Zea mays",
      "suitability_score": 0.92,
      ...
    }
  ],
  "average_annual_rainfall": 850.5,
  "soil_type": "Humic Nitisols",
  "humanized_summary": "Great news! Your location in Nairobi..."
}
```

### 2. Crop Analysis
```bash
POST /api/crop-analysis
```

**Request:**
```json
{
  "crop_name": "Maize",
  "location": "Kisumu, Kenya",
  "humanize": true
}
```

**Response:**
```json
{
  "crop_name": "Maize",
  "scientific_name": "Zea mays",
  "location": "Kisumu, Kenya",
  "coordinates": {...},
  "optimal_conditions": {
    "temperature_min": 18,
    "temperature_max": 32,
    "rainfall_min": 500,
    "rainfall_max": 1200,
    ...
  },
  "best_planting_time": "March-April",
  "growth_duration_days": 120,
  "suitability_score": 0.88,
  "suitability_factors": {...}
}
```

### 3. Smart Route
```bash
POST /api/smart-route
```

**Request:**
```json
{
  "start_point": "Nairobi",
  "end_point": "Nakuru"
}
```

**Response:**
```json
{
  "start_point": "Nairobi",
  "end_point": "Nakuru",
  "start_coordinates": {...},
  "end_coordinates": {...},
  "route_geometry": {...},
  "distance_km": 156.3,
  "estimated_time_minutes": 180,
  "rainfall_forecast": 25.5,
  "vulnerable_roads_avoided": 12,
  "weather_alert": true,
  "alternative_routes": [...]
}
```

### 4. 🤖 Agribricks AI Assistant
```bash
POST /api/agribricks-ai
```

**Request:**
```json
{
  "question": "How do I control aphids on my tomato plants naturally?",
  "location": "Central Kenya",
  "crop_type": "tomatoes",
  "language": "en"
}
```

**Response:**
```json
{
  "question": "How do I control aphids on my tomato plants naturally?",
  "answer": "🎯 **Direct Answer**\nAphids on tomatoes can be effectively controlled using several natural methods...\n\n📋 **Action Steps**\n1. Spray plants with neem oil solution (2-3ml per liter of water)\n2. Introduce beneficial insects like ladybugs and lacewings\n3. Use companion planting with marigolds and basil...",
  "confidence_score": 0.92,
  "sources": [
    "Agricultural best practices database",
    "Integrated pest management protocols"
  ],
  "recommendations": [
    "Apply neem oil spray early morning or evening",
    "Monitor plants weekly for early detection",
    "Maintain proper plant spacing for air circulation"
  ],
  "location_context": "Central Kenya",
  "crop_context": "tomatoes"
}
```

### 5. 🔬 Crop Disease Detection (NEW!)
```bash
POST /api/crop-disease-detection
```

**Request (Multipart Form):**
```bash
curl -X POST "http://localhost:8000/api/crop-disease-detection" \
  -F "image=@plant_photo.jpg" \
  -F "crop_type=tomato" \
  -F "location=Central Kenya" \
  -F "additional_symptoms=Brown spots, yellowing leaves"
```

**Response:**
```json
{
  "diagnosis": "Early Blight (Alternaria solani) - Fungal infection commonly affecting tomatoes",
  "confidence": "High",
  "severity": "Moderate",
  "treatment_recommendations": [
    "Apply copper-based fungicide spray every 7-10 days",
    "Remove and destroy affected leaves immediately",
    "Improve air circulation around plants",
    "Apply neem oil as organic alternative"
  ],
  "management_strategy": [
    "Implement crop rotation with non-solanaceous crops",
    "Mulch around plants to prevent soil splash",
    "Water at soil level to avoid wetting leaves",
    "Plant resistant tomato varieties next season"
  ],
  "crop_type": "tomato",
  "location": "Central Kenya",
  "model_used": "meta-llama/llama-4-scout-17b-16e-instruct",
  "full_analysis": "Detailed pathological analysis..."
}
```

**Health Checks:**
```bash
GET /api/agribricks-ai/health
GET /api/examples  # Get example questions and usage tips
```

## ML Models

### Rainfall Prediction
- **Classification**: Will it rain? (>1mm threshold)
  - XGBoost Classifier
  - **Features include AEZ (location)** as a primary feature
  - Additional features: Temperature, humidity, solar radiation, lagged values, cyclical month encoding
  - One-hot encoded AEZ for better zone-specific predictions
  - Evaluation: AUC-ROC score
  
- **Regression**: How much rain?
  - XGBoost Regressor
  - Same feature set including location
  - Evaluation: RMSE, R² score

### Crop Recommendation
- **Random Forest Classifier**
- **AEZ (location) is a primary feature** - critical for Kenya's diverse climate zones
- Features: AEZ encoding, temperature, rainfall, humidity, soil properties, crop requirements
- Multi-class classification (Not Suitable, Marginal, Highly Suitable)
- K-Fold cross-validation (k=5)

### Model Performance
All models evaluated using:
- K-Fold Cross Validation (5 folds)
- AUC-ROC for classification
- RMSE for regression
- Train-test split (80-20)

## Database Schema

### Tables
1. **prediction_logs**: Store all API predictions
2. **location_cache**: Cache geocoding results
3. **road_cache**: Cache road network data

### Migrations
```bash
# Create tables automatically on first run
# Or manually:
pipenv shell
python -c "from api.database import Base, engine; Base.metadata.create_all(engine)"
```

## Configuration

Key settings in `.env`:

```bash
# API Keys
ORS_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_groq_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
and when running on docker remember to change from @localhost to @db

# Model Settings
RAINFALL_THRESHOLD=20.0  # mm for road vulnerability
ENABLE_ROAD_CACHE=True
```

## Development

### Running Tests

### Adding New Models
1. Create training notebook in `notebooks/`
2. Train and save model to `models/`
3. Add loading logic to `api/ml_models.py`
4. Create endpoint in `api/main.py`
5. Update schemas in `api/schemas.py`

## Deployment

### Production Checklist
- [ ] Set DEBUG=False in .env
- [ ] Use strong database passwords
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Enable database backups
- [ ] Use production-grade WSGI server

### Deploy to Cloud
Deployment to the cloud.
On render create a postgres instance and copy the internal url
Create a new webservice and configure the following:
- Connect your GitHub repository.

- Name: Give it a name (e.g., agri-mobility-api).

- Region: Choose the one closest to you (e.g., Frankfurt or Oregon).

- Branch: main (or whatever branch your code is on).

- Configure the following envirinment variables:

- ORS_API_KEY -> From OpenRouteService
- OPENROUTER_API_KEY -> From OpenRouter
- RAINFALL_THRESHOLD -> 20.0
- ORS_BASE_URL -> https://api.openrouteservice.org,
- OPENROUTER_MODEL -> anthropic/claude-3-haiku,
- DATA_DIR -> ./data
- MODELS_DIR -> ./models

- After successful configuration render logs should display the following:
![render logs](Screenshots/render%20logs.png)

#### Live url found at: "https://smart-climate-agriculture-machine.onrender.com" to test the apis add  "/docs" to the url
![Live on Render](Screenshots/live%20api.png)

## Troubleshooting

### Models not loading
- Verify all .pkl files exist in `models/` directory
- Check file permissions
- Ensure models were trained with same sklearn version

### Geocoding fails
- Check internet connection
- Verify location name format
- Use full location names (e.g., "Nairobi, Kenya")

### Routing errors
- Verify ORS_API_KEY is set correctly
- Check API rate limits
- Ensure coordinates are valid

### Database connection issues
- Verify DATABASE_URL is correct
- Check PostgreSQL is running
- Ensure database exists

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file

## Support

For issues and questions:
- on X: @mendykev

## Acknowledgments

- EcoCrop database for crop information
- NASA POWER for weather data
- OpenRouteService for routing
- OpenStreetMap for road data
