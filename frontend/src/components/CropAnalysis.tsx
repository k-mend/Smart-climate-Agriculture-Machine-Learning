import { useState } from 'react';
import { Search } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface CropResult {
  crop_name: string;
  scientific_name: string;
  location: string;
  optimal_conditions: {
    temperature_min: number;
    temperature_max: number;
    rainfall_min: number;
    rainfall_max: number;
  };
  best_planting_time: string;
  growth_duration_days: number;
  suitability_score: number;
  humanized_summary?: string;
}

export default function CropAnalysis() {
  const [cropName, setCropName] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<CropResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/crop-analysis`, {
        crop_name: cropName,
        location,
        humanize: true
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze crop. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Crop Analysis</h2>
        <p>Get detailed insights about growing a specific crop in your location</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="cropName">Crop Name</label>
          <input
            id="cropName"
            type="text"
            placeholder="e.g., Maize, Tomatoes, Coffee"
            value={cropName}
            onChange={(e) => setCropName(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Location</label>
          <input
            id="location"
            type="text"
            placeholder="e.g., Kisumu, Kenya"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <Search size={20} />
          {loading ? 'Analyzing...' : 'Analyze Crop'}
        </button>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing crop suitability...</p>
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
            <h3>Crop Information</h3>
            <div className="result-item">
              <span className="result-label">Common Name:</span>
              <span className="result-value">{result.crop_name}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Scientific Name:</span>
              <span className="result-value" style={{ fontStyle: 'italic' }}>{result.scientific_name}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Location:</span>
              <span className="result-value">{result.location}</span>
            </div>
          </div>

          <div className="result-section">
            <h3>Growing Conditions</h3>
            <div className="result-item">
              <span className="result-label">Temperature Range:</span>
              <span className="result-value">
                {result.optimal_conditions.temperature_min}°C - {result.optimal_conditions.temperature_max}°C
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Rainfall Range:</span>
              <span className="result-value">
                {result.optimal_conditions.rainfall_min} - {result.optimal_conditions.rainfall_max} mm/year
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Growth Duration:</span>
              <span className="result-value">{result.growth_duration_days} days</span>
            </div>
            <div className="result-item">
              <span className="result-label">Best Planting Time:</span>
              <span className="result-value">{result.best_planting_time}</span>
            </div>
          </div>

          <div className="result-section">
            <h3>Suitability Assessment</h3>
            <div style={{ textAlign: 'center', padding: '1rem' }}>
              <div style={{
                fontSize: '3rem',
                fontWeight: 'bold',
                color: result.suitability_score > 0.7 ? '#4A7C59' : result.suitability_score > 0.5 ? '#D4A574' : '#C62828'
              }}>
                {(result.suitability_score * 100).toFixed(0)}%
              </div>
              <div style={{ marginTop: '0.5rem', color: '#666' }}>
                {result.suitability_score > 0.7 ? 'Highly Suitable' :
                 result.suitability_score > 0.5 ? 'Moderately Suitable' : 'Not Recommended'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
