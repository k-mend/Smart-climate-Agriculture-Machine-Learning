# Climate-Smart Agriculture & Smart Mobility API

An ML-powered FastAPI backend for agricultural insights and intelligent routing based on weather predictions and road conditions.

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
- **AI Enhancement**: OpenRouter (Claude)

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
│   └── ai_humanizer.py      # AI response enhancement
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

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd climate-agri-mobility
```

2. **Create and configure .env file**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install dependencies with Pipenv**
```bash
pip install pipenv
pipenv install
pipenv shell
```

4. **Or use Docker Compose (recommended)**
```bash
docker-compose up -d
```

## Training Models

### Step 1: Prepare Your Data
Place your datasets in the `data/` directory:
- `cleaned_ecocrop.csv` - Crop database (lowercase columns)
- `merged_aez_weather.csv` - Weather data with AEZ zones (lowercase columns)

### Step 2: Train Models
```bash
# Activate virtual environment
pipenv shell

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
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Using Pipenv
```bash
pipenv shell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

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

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Model Settings
RAINFALL_THRESHOLD=20.0  # mm for road vulnerability
ENABLE_ROAD_CACHE=True
```

## Development

### Running Tests
```bash
pipenv shell
pytest tests/
```

### Code Formatting
```bash
black api/
flake8 api/
```

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
```bash
# Build and push Docker image
docker build -t climate-agri-api:latest .
docker tag climate-agri-api:latest your-registry/climate-agri-api:latest
docker push your-registry/climate-agri-api:latest

# Deploy using your cloud provider's tools
```

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
- Email: kmend8980@gmail.com

## Acknowledgments

- EcoCrop database for crop information
- NASA POWER for weather data
- OpenRouteService for routing
- OpenStreetMap for road data
