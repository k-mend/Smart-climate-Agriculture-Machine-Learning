import { useState } from 'react';
import { Search } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface CropRecommendation {
  crop_name: string;
  scientific_name: string;
  suitability_score: number;
}

interface LocationResult {
  location: string;
  aez: string;
  best_planting_times: string[];
  recommended_crops: CropRecommendation[];
  average_annual_rainfall: number;
  soil_type?: string;
  humanized_summary?: string;
}

export default function LocationAnalysis() {
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<LocationResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/location-analysis`, {
        location,
        humanize: true
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze location. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Location Analysis</h2>
        <p>Discover the best crops and planting times for your location</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            type="text"
            placeholder="e.g., Nairobi, Kenya"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <Search size={20} />
          {loading ? 'Analyzing...' : 'Analyze Location'}
        </button>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing climate and soil conditions...</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          {result.humanized_summary && (
            <div className="result-section" style={{ background: '#FFF9E6', borderLeft: '4px solid #D4A574' }}>
              <h3>Summary</h3>
              <p>{result.humanized_summary}</p>
            </div>
          )}

          <div className="result-section">
            <h3>Location Details</h3>
            <div className="result-item">
              <span className="result-label">Location:</span>
              <span className="result-value">{result.location}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Climate Zone:</span>
              <span className="result-value">{result.aez}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Annual Rainfall:</span>
              <span className="result-value">{result.average_annual_rainfall.toFixed(0)} mm</span>
            </div>
            {result.soil_type && (
              <div className="result-item">
                <span className="result-label">Soil Type:</span>
                <span className="result-value">{result.soil_type}</span>
              </div>
            )}
          </div>

          <div className="result-section">
            <h3>Best Planting Times</h3>
            {result.best_planting_times.map((time, index) => (
              <div key={index} className="result-item">
                {time}
              </div>
            ))}
          </div>

          <div className="result-section">
            <h3>Recommended Crops</h3>
            <div className="crop-list">
              {result.recommended_crops.slice(0, 5).map((crop, index) => (
                <div key={index} className="crop-card">
                  <div className="crop-name">{crop.crop_name}</div>
                  <div style={{ fontSize: '0.875rem', color: '#666', fontStyle: 'italic' }}>
                    {crop.scientific_name}
                  </div>
                  <div className="suitability-score">
                    Suitability: {(crop.suitability_score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
