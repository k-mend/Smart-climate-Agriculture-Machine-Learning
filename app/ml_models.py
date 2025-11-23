import joblib  # Using joblib instead of pickle for compressed models
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)

# Valid AEZ zones for Kenya
VALID_AEZ_ZONES = [
    'Highlands (Humid)',
    'Upper Midlands (High Potential)',
    'Lower Midlands (Semi-Arid)',
    'Coastal Lowlands (Humid)',
    'Arid Lowlands (Arid)'
]


class MLModels:
    """Handles loading and inference for all ML models (using joblib compression)"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_cols = {}
        self.crop_database = None
        self.weather_by_aez = None
        self.models_loaded = False
        # Column name mappings (will be detected from actual data)
        self.crop_columns = {}
        self.weather_columns = {}
        
    def load_models(self):
        """Load all trained models and preprocessors (joblib compressed)"""
        try:
            models_dir = Path(settings.MODELS_DIR)
            data_dir = Path(settings.DATA_DIR)
            
            # Load rainfall models
            self.models['rainfall_classifier'] = joblib.load(
                models_dir / 'rainfall_classifier.joblib'
            )
            self.models['rainfall_regressor'] = joblib.load(
                models_dir / 'rainfall_regressor.joblib'
            )
            self.scalers['rainfall'] = joblib.load(
                models_dir / 'scaler_rainfall.joblib'
            )
            self.encoders['aez_label'] = joblib.load(
                models_dir / 'aez_label_encoder.joblib'
            )
            self.encoders['aez_onehot'] = joblib.load(
                models_dir / 'aez_onehot_encoder.joblib'
            )
            self.feature_cols['rainfall'] = joblib.load(
                models_dir / 'rainfall_feature_columns.joblib'
            )
            
            # Load crop recommendation models
            self.models['crop_recommendation'] = joblib.load(
                models_dir / 'crop_recommendation_model.joblib'
            )
            self.scalers['crop'] = joblib.load(
                models_dir / 'scaler_crop.joblib'
            )
            self.encoders['crop_label'] = joblib.load(
                models_dir / 'crop_label_encoder.joblib'
            )
            self.encoders['aez_label_crop'] = joblib.load(
                models_dir / 'aez_label_encoder_crop.joblib'
            )
            self.encoders['aez_onehot_crop'] = joblib.load(
                models_dir / 'aez_onehot_encoder_crop.joblib'
            )
            self.feature_cols['crop'] = joblib.load(
                models_dir / 'crop_feature_columns.joblib'
            )
            
            # Load reference data from DATA directory
            self.crop_database = pd.read_csv(data_dir / 'cleaned_ecocrop.csv')
            logger.info(f"Loaded crop database with columns: {self.crop_database.columns.tolist()}")
            
            # Detect and map crop column names
            self._detect_crop_columns()
            
            # Load weather data and compute AEZ summaries
            weather_data = pd.read_csv(data_dir / 'merged_aez_weather.csv')
            logger.info(f"Loaded weather data with columns: {weather_data.columns.tolist()}")
            
            # Detect and map weather column names
            self._detect_weather_columns(weather_data)
            
            # Compute weather summaries by AEZ
            self.weather_by_aez = self._compute_weather_by_aez(weather_data)
            logger.info(f"Weather by AEZ computed: {self.weather_by_aez}")
            
            self.models_loaded = True
            logger.info("All models loaded successfully (joblib compressed)")
            logger.info(f"Loaded {len(self.crop_database)} crops")
            logger.info(f"AEZ zones in weather data: {self.weather_by_aez.keys() if isinstance(self.weather_by_aez, dict) else 'DataFrame'}")
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def _detect_crop_columns(self):
        """Detect actual column names in crop database"""
        cols = self.crop_database.columns.tolist()
        
        # Create mapping from standard names to actual column names
        # Check both uppercase and lowercase variants
        column_mappings = {
            'comname': ['COMNAME', 'comname', 'common_name', 'name', 'crop_name'],
            'scientificname': ['ScientificName', 'scientificname', 'SCIENTIFICNAME', 'scientific_name'],
            'tmin': ['TMIN', 'tmin', 't_min', 'temp_min'],
            'tmax': ['TMAX', 'tmax', 't_max', 'temp_max'],
            'topmn': ['TOPMN', 'topmn', 'topt_min', 'temp_opt_min'],
            'topmx': ['TOPMX', 'topmx', 'topt_max', 'temp_opt_max'],
            'rmin': ['RMIN', 'rmin', 'r_min', 'rain_min', 'rainfall_min'],
            'rmax': ['RMAX', 'rmax', 'r_max', 'rain_max', 'rainfall_max'],
            'ropmn': ['ROPMN', 'ropmn', 'ropt_min', 'rain_opt_min'],
            'ropmx': ['ROPMX', 'ropmx', 'ropt_max', 'rain_opt_max'],
            'phopmn': ['PHOPMN', 'phopmn', 'ph_min', 'phmin'],
            'phopmx': ['PHOPMX', 'phopmx', 'ph_max', 'phmax'],
            'gmin': ['GMIN', 'gmin', 'growth_min', 'days_min'],
            'gmax': ['GMAX', 'gmax', 'growth_max', 'days_max'],
        }
        
        for standard_name, possible_names in column_mappings.items():
            for possible in possible_names:
                if possible in cols:
                    self.crop_columns[standard_name] = possible
                    break
        
        logger.info(f"Detected crop column mappings: {self.crop_columns}")
    
    def _detect_weather_columns(self, weather_data: pd.DataFrame):
        """Detect actual column names in weather data"""
        cols = weather_data.columns.tolist()
        
        # Check both uppercase and lowercase variants
        column_mappings = {
            'aez': ['AEZ', 'aez', 'zone', 'agro_ecological_zone'],
            'prectotcorr': ['PRECTOTCORR', 'prectotcorr', 'precipitation', 'rainfall', 'rain'],
            't2m': ['T2M', 't2m', 'temperature', 'temp'],
            'rh2m': ['RH2M', 'rh2m', 'humidity', 'relative_humidity'],
            'allsky_sfc_sw_dwn': ['ALLSKY_SFC_SW_DWN', 'allsky_sfc_sw_dwn', 'solar_radiation', 'radiation'],
            'date': ['date', 'DATE', 'datetime', 'time'],
        }
        
        for standard_name, possible_names in column_mappings.items():
            for possible in possible_names:
                if possible in cols:
                    self.weather_columns[standard_name] = possible
                    break
        
        logger.info(f"Detected weather column mappings: {self.weather_columns}")
    
    def _get_crop_value(self, crop_row, standard_name, default=None):
        """Get value from crop row using detected column name"""
        actual_col = self.crop_columns.get(standard_name)
        if actual_col and actual_col in crop_row.index:
            val = crop_row[actual_col]
            if pd.notna(val):
                return val
        return default
    
    def _compute_weather_by_aez(self, weather_data: pd.DataFrame) -> Dict[str, Dict]:
        """Compute weather statistics by AEZ from raw weather data"""
        try:
            aez_col = self.weather_columns.get('aez', 'aez')
            precip_col = self.weather_columns.get('prectotcorr', 'prectotcorr')
            temp_col = self.weather_columns.get('t2m', 't2m')
            humidity_col = self.weather_columns.get('rh2m', 'rh2m')
            solar_col = self.weather_columns.get('allsky_sfc_sw_dwn', 'allsky_sfc_sw_dwn')
            date_col = self.weather_columns.get('date', 'date')
            
            # Convert date if present
            if date_col in weather_data.columns:
                weather_data[date_col] = pd.to_datetime(weather_data[date_col])
                weather_data['year'] = weather_data[date_col].dt.year
            
            # Get unique AEZ zones
            unique_aez = weather_data[aez_col].unique()
            logger.info(f"Found AEZ zones in data: {unique_aez}")
            
            # Compute statistics for each AEZ
            weather_by_aez = {}
            
            for aez in unique_aez:
                aez_data = weather_data[weather_data[aez_col] == aez]
                
                # If we have yearly data, compute annual totals first for rainfall
                if 'year' in weather_data.columns:
                    annual_precip = aez_data.groupby('year')[precip_col].sum()
                    avg_rainfall = annual_precip.mean()
                    rainfall_std = annual_precip.std()
                else:
                    # Assume daily data, multiply by 365 for annual estimate
                    avg_rainfall = aez_data[precip_col].mean() * 365
                    rainfall_std = aez_data[precip_col].std() * np.sqrt(365)
                
                weather_by_aez[aez] = {
                    'avg_temperature': float(aez_data[temp_col].mean()) if temp_col in aez_data.columns else 25.0,
                    'avg_rainfall': float(avg_rainfall) if not pd.isna(avg_rainfall) else 1000.0,
                    'avg_humidity': float(aez_data[humidity_col].mean()) if humidity_col in aez_data.columns else 70.0,
                    'avg_solar': float(aez_data[solar_col].mean()) if solar_col in aez_data.columns else 200.0,
                    'temp_variability': float(aez_data[temp_col].std()) if temp_col in aez_data.columns else 2.0,
                    'rainfall_variability': float(rainfall_std) if not pd.isna(rainfall_std) else 200.0
                }
            
            logger.info(f"Computed weather for AEZ zones: {list(weather_by_aez.keys())}")
            return weather_by_aez
            
        except Exception as e:
            logger.error(f"Error computing weather by AEZ: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def get_aez_climate_data(self, aez: str) -> Dict:
        """Get climate statistics for a specific AEZ (location)"""
        # Try exact match first
        if isinstance(self.weather_by_aez, dict) and aez in self.weather_by_aez:
            return self.weather_by_aez[aez]
        
        # Try case-insensitive match
        if isinstance(self.weather_by_aez, dict):
            for key in self.weather_by_aez.keys():
                if key.lower() == aez.lower():
                    return self.weather_by_aez[key]
        
        logger.warning(f"No climate data found for AEZ: {aez}, using defaults")
        return self._get_default_climate_data(aez)
    
    def _get_default_climate_data(self, aez: str) -> Dict:
        """Get default climate data based on AEZ type"""
        defaults = {
            'Highlands (Humid)': {
                'avg_temperature': 18.0, 'avg_rainfall': 1500.0,
                'avg_humidity': 75.0, 'avg_solar': 180.0,
                'temp_variability': 2.0, 'rainfall_variability': 300.0
            },
            'Upper Midlands (High Potential)': {
                'avg_temperature': 22.0, 'avg_rainfall': 1200.0,
                'avg_humidity': 70.0, 'avg_solar': 200.0,
                'temp_variability': 2.5, 'rainfall_variability': 250.0
            },
            'Lower Midlands (Semi-Arid)': {
                'avg_temperature': 26.0, 'avg_rainfall': 700.0,
                'avg_humidity': 55.0, 'avg_solar': 220.0,
                'temp_variability': 3.0, 'rainfall_variability': 200.0
            },
            'Coastal Lowlands (Humid)': {
                'avg_temperature': 28.0, 'avg_rainfall': 1100.0,
                'avg_humidity': 80.0, 'avg_solar': 210.0,
                'temp_variability': 2.0, 'rainfall_variability': 250.0
            },
            'Arid Lowlands (Arid)': {
                'avg_temperature': 30.0, 'avg_rainfall': 350.0,
                'avg_humidity': 40.0, 'avg_solar': 240.0,
                'temp_variability': 4.0, 'rainfall_variability': 150.0
            }
        }
        
        # Try exact match
        if aez in defaults:
            return defaults[aez]
        
        # Try partial match
        for key in defaults:
            if key.lower() in aez.lower() or aez.lower() in key.lower():
                return defaults[key]
        
        # Return generic default
        return {
            'avg_temperature': 25.0, 'avg_rainfall': 1000.0,
            'avg_humidity': 65.0, 'avg_solar': 200.0,
            'temp_variability': 2.5, 'rainfall_variability': 200.0
        }
    
    def predict_rainfall(self, aez: str, current_month: int = None) -> Dict:
        """Predict rainfall for a specific AEZ (location)"""
        if current_month is None:
            current_month = datetime.now().month
            
        try:
            climate_data = self.get_aez_climate_data(aez)
            
            # Encode AEZ
            try:
                aez_encoded = self.encoders['aez_label'].transform([aez])[0]
            except ValueError:
                logger.warning(f"Unknown AEZ: {aez}, using default encoding")
                aez_encoded = 0
            
            # Get one-hot encoding for AEZ
            try:
                aez_onehot = self.encoders['aez_onehot'].transform([[aez]])[0]
            except ValueError:
                aez_onehot = np.zeros(len(self.encoders['aez_onehot'].categories_[0]))
            
            monthly_predictions = {}
            next_7days_total = 0
            
            for i in range(12):
                month = ((current_month + i - 1) % 12) + 1
                day_of_year = (month - 1) * 30 + 15
                week_of_year = (day_of_year // 7) + 1
                
                month_sin = np.sin(2 * np.pi * month / 12)
                month_cos = np.cos(2 * np.pi * month / 12)
                
                base_features = {
                    't2m': climate_data['avg_temperature'],
                    'rh2m': climate_data['avg_humidity'],
                    'allsky_sfc_sw_dwn': climate_data['avg_solar'],
                    'month': month,
                    'day_of_year': day_of_year,
                    'week_of_year': week_of_year,
                    'month_sin': month_sin,
                    'month_cos': month_cos,
                    'aez_encoded': aez_encoded,
                    'rainfall_lag_1': climate_data['avg_rainfall'] / 365,
                    'rainfall_lag_3': climate_data['avg_rainfall'] / 365,
                    'rainfall_lag_7': climate_data['avg_rainfall'] / 365,
                    'rainfall_lag_14': climate_data['avg_rainfall'] / 365,
                    'temp_lag_1': climate_data['avg_temperature'],
                    'temp_lag_3': climate_data['avg_temperature'],
                    'temp_lag_7': climate_data['avg_temperature'],
                    'humidity_lag_1': climate_data['avg_humidity'],
                    'humidity_lag_3': climate_data['avg_humidity'],
                    'humidity_lag_7': climate_data['avg_humidity'],
                    'rainfall_7d_avg': climate_data['avg_rainfall'] / 52,
                    'rainfall_14d_avg': climate_data['avg_rainfall'] / 26,
                    'rainfall_30d_avg': climate_data['avg_rainfall'] / 12,
                    'rainfall_7d_std': climate_data['rainfall_variability'] / 52,
                    'rainfall_14d_std': climate_data['rainfall_variability'] / 26,
                    'temp_7d_avg': climate_data['avg_temperature'],
                    'temp_14d_avg': climate_data['avg_temperature']
                }
                
                # Create feature array using DataFrame to preserve feature names
                feature_values = []
                for col in self.feature_cols['rainfall']:
                    if col.startswith('aez_') and col != 'aez_encoded':
                        try:
                            categories = list(self.encoders['aez_onehot'].categories_[0])
                            aez_name = col.replace('aez_', '')
                            if aez_name in categories:
                                idx = categories.index(aez_name)
                                feature_values.append(aez_onehot[idx])
                            else:
                                feature_values.append(0)
                        except (ValueError, IndexError):
                            feature_values.append(0)
                    else:
                        feature_values.append(base_features.get(col, 0))
                
                # Create DataFrame with feature names to avoid sklearn warning
                X = pd.DataFrame([feature_values], columns=self.feature_cols['rainfall'])
                X_scaled = self.scalers['rainfall'].transform(X)
                
                will_rain = bool(self.models['rainfall_classifier'].predict(X_scaled)[0])
                rainfall_amount = float(max(0, self.models['rainfall_regressor'].predict(X_scaled)[0]))
                
                # Adjust for seasonality
                if month in [3, 4, 5, 10, 11]:
                    rainfall_amount *= 1.5
                elif month in [1, 2, 6, 7, 8, 9]:
                    rainfall_amount *= 0.6
                
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                
                monthly_predictions[f"month_{month}"] = {
                    "month_name": month_names[month - 1],
                    "will_rain": will_rain,
                    "amount_mm": round(rainfall_amount, 2)
                }
                
                if i == 0:
                    next_7days_total = rainfall_amount * 7 / 30
            
            return {
                "aez": aez,
                "monthly_forecast": monthly_predictions,
                "next_7days_total": round(next_7days_total, 2),
                "avg_annual_rainfall": climate_data['avg_rainfall'],
                "avg_temperature": climate_data['avg_temperature']
            }
            
        except Exception as e:
            logger.error(f"Error predicting rainfall: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def predict_planting_times(self, rainfall_predictions: Dict) -> List[str]:
        """Determine best planting times based on rainfall onset"""
        monthly_forecast = rainfall_predictions['monthly_forecast']
        planting_months = []
        
        months_data = []
        for key, data in monthly_forecast.items():
            month_num = int(key.split('_')[1])
            months_data.append({
                'month': month_num,
                'name': data['month_name'],
                'rainfall': data['amount_mm']
            })
        
        months_data.sort(key=lambda x: x['month'])
        
        for i in range(len(months_data)):
            current = months_data[i]
            prev = months_data[i - 1] if i > 0 else months_data[-1]
            
            if current['rainfall'] > prev['rainfall'] + 20 and current['rainfall'] > 50:
                planting_months.append(f"{current['name']} (onset of rains)")
        
        known_seasons = []
        march_rain = next((m['rainfall'] for m in months_data if m['month'] == 3), 0)
        oct_rain = next((m['rainfall'] for m in months_data if m['month'] == 10), 0)
        
        if march_rain > 30:
            known_seasons.append("March-April (Long rains)")
        if oct_rain > 30:
            known_seasons.append("October-November (Short rains)")
        
        result = list(set(planting_months + known_seasons))
        
        if not result:
            result = ["March-April (Long rains)", "October-November (Short rains)"]
        
        return result[:3]
    
    def recommend_crops(self, aez: str, temperature: float = None, rainfall: float = None) -> List[Dict]:
        """Recommend suitable crops for a specific AEZ (location)"""
        try:
            climate_data = self.get_aez_climate_data(aez)
            
            if temperature is None:
                temperature = climate_data['avg_temperature']
            if rainfall is None:
                rainfall = climate_data['avg_rainfall']
            
            recommendations = []
            
            for _, crop in self.crop_database.iterrows():
                # Get values using detected column names
                tmin = self._get_crop_value(crop, 'tmin', 0)
                tmax = self._get_crop_value(crop, 'tmax', 50)
                topmn = self._get_crop_value(crop, 'topmn', tmin)
                topmx = self._get_crop_value(crop, 'topmx', tmax)
                rmin = self._get_crop_value(crop, 'rmin', 0)
                rmax = self._get_crop_value(crop, 'rmax', 5000)
                ropmn = self._get_crop_value(crop, 'ropmn', rmin)
                ropmx = self._get_crop_value(crop, 'ropmx', rmax)
                comname = self._get_crop_value(crop, 'comname', 'Unknown')
                sciname = self._get_crop_value(crop, 'scientificname', 'N/A')
                
                # Check suitability
                temp_optimal = topmn <= temperature <= topmx
                temp_absolute = tmin <= temperature <= tmax
                rain_optimal = ropmn <= rainfall <= ropmx
                rain_absolute = rmin <= rainfall <= rmax
                
                if not (temp_absolute and rain_absolute):
                    continue
                
                # Calculate suitability score
                temp_range = tmax - tmin if tmax > tmin else 1
                rain_range = rmax - rmin if rmax > rmin else 1
                
                temp_score = 1.0 if temp_optimal else 0.7
                rain_score = 1.0 if rain_optimal else 0.7
                
                temp_center = (topmn + topmx) / 2
                temp_dist_score = max(0, 1 - abs(temperature - temp_center) / temp_range)
                
                rain_center = (ropmn + ropmx) / 2
                rain_dist_score = max(0, 1 - abs(rainfall - rain_center) / rain_range)
                
                suitability = (temp_score * 0.3 + rain_score * 0.3 + 
                              temp_dist_score * 0.2 + rain_dist_score * 0.2)
                
                recommendations.append({
                    "crop_name": comname,
                    "scientific_name": sciname,
                    "suitability_score": round(float(max(0, min(1, suitability))), 3),
                    "temperature_range": {
                        "min": float(tmin),
                        "max": float(tmax),
                        "optimal_min": float(topmn),
                        "optimal_max": float(topmx)
                    },
                    "rainfall_range": {
                        "min": float(rmin),
                        "max": float(rmax),
                        "optimal_min": float(ropmn),
                        "optimal_max": float(ropmx)
                    }
                })
            
            recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
            return recommendations[:10]
            
        except Exception as e:
            logger.error(f"Error recommending crops: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def get_crop_info(self, crop_name: str) -> Optional[Dict]:
        """Get detailed information about a specific crop"""
        try:
            comname_col = self.crop_columns.get('comname', 'comname')
            
            # Try exact match
            crop = self.crop_database[
                self.crop_database[comname_col].str.lower() == crop_name.lower()
            ]
            
            if crop.empty:
                # Try partial match
                crop = self.crop_database[
                    self.crop_database[comname_col].str.lower().str.contains(crop_name.lower(), na=False)
                ]
            
            if crop.empty:
                return None
            
            crop = crop.iloc[0]
            
            return {
                "crop_name": self._get_crop_value(crop, 'comname', crop_name),
                "scientific_name": self._get_crop_value(crop, 'scientificname', 'N/A'),
                "temp_min": float(self._get_crop_value(crop, 'tmin', 10)),
                "temp_max": float(self._get_crop_value(crop, 'tmax', 40)),
                "temp_opt_min": float(self._get_crop_value(crop, 'topmn', 15)),
                "temp_opt_max": float(self._get_crop_value(crop, 'topmx', 35)),
                "rainfall_min": float(self._get_crop_value(crop, 'rmin', 200)),
                "rainfall_max": float(self._get_crop_value(crop, 'rmax', 3000)),
                "rainfall_opt_min": float(self._get_crop_value(crop, 'ropmn', 400)),
                "rainfall_opt_max": float(self._get_crop_value(crop, 'ropmx', 2000)),
                "ph_min": float(self._get_crop_value(crop, 'phopmn', 5.5)),
                "ph_max": float(self._get_crop_value(crop, 'phopmx', 7.5)),
                "growth_duration_min": int(self._get_crop_value(crop, 'gmin', 60)),
                "growth_duration_max": int(self._get_crop_value(crop, 'gmax', 120)),
                "growth_duration": int((self._get_crop_value(crop, 'gmin', 60) + 
                                       self._get_crop_value(crop, 'gmax', 120)) / 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting crop info: {str(e)}")
            return None
    
    def calculate_crop_suitability(
        self, 
        crop_name: str, 
        aez: str, 
        lat: float = None, 
        lon: float = None
    ) -> Dict:
        """Calculate how suitable a location (AEZ) is for a specific crop"""
        crop_info = self.get_crop_info(crop_name)
        if not crop_info:
            return {"score": 0.0, "factors": {"error": "Crop not found"}}
        
        climate_data = self.get_aez_climate_data(aez)
        temperature = climate_data['avg_temperature']
        rainfall = climate_data['avg_rainfall']
        
        factors = {}
        scores = []
        
        if crop_info['temp_opt_min'] <= temperature <= crop_info['temp_opt_max']:
            factors['temperature'] = "Optimal"
            scores.append(1.0)
        elif crop_info['temp_min'] <= temperature <= crop_info['temp_max']:
            factors['temperature'] = "Suitable"
            scores.append(0.7)
        else:
            factors['temperature'] = "Not suitable"
            scores.append(0.3)
        
        # Rainfall suitability
        if crop_info['rainfall_opt_min'] <= rainfall <= crop_info['rainfall_opt_max']:
            factors['rainfall'] = "Optimal"
            scores.append(1.0)
        elif crop_info['rainfall_min'] <= rainfall <= crop_info['rainfall_max']:
            factors['rainfall'] = "Suitable"
            scores.append(0.7)
        else:
            factors['rainfall'] = "Not suitable"
            scores.append(0.3)
        
        # AEZ factor
        factors['aez'] = aez
        factors['climate_zone'] = "Matched to local conditions"
        
        return {
            "score": round(sum(scores) / len(scores), 3) if scores else 0.0,
            "factors": factors
        }
    
    def get_best_planting_time_for_crop(self, crop_info: Dict, aez: str) -> str:
        """Determine best planting time for specific crop in given AEZ"""
        try:
            rainfall_pred = self.predict_rainfall(aez)
            planting_times = self.predict_planting_times(rainfall_pred)
            
            if planting_times:
                return planting_times[0]
        except Exception as e:
            logger.error(f"Error getting planting time: {str(e)}")
        
        return "March-April (Long rains) or October-November (Short rains)"
