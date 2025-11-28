import { useState } from 'react';
import { Navigation, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface RouteResult {
  start_point: string;
  end_point: string;
  distance_km: number;
  estimated_time_minutes: number;
  rainfall_forecast: number;
  vulnerable_roads_avoided: number;
  weather_alert: boolean;
}

export default function SmartRoute() {
  const [startPoint, setStartPoint] = useState('');
  const [endPoint, setEndPoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<RouteResult | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/smart-route`, {
        start_point: startPoint,
        end_point: endPoint
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to calculate route. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Smart Route Planning</h2>
        <p>Get weather-aware routes that avoid vulnerable roads during rainfall</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="startPoint">Starting Point</label>
          <input
            id="startPoint"
            type="text"
            placeholder="e.g., Nairobi"
            value={startPoint}
            onChange={(e) => setStartPoint(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="endPoint">Destination</label>
          <input
            id="endPoint"
            type="text"
            placeholder="e.g., Nakuru"
            value={endPoint}
            onChange={(e) => setEndPoint(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <Navigation size={20} />
          {loading ? 'Calculating...' : 'Calculate Route'}
        </button>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Calculating optimal route...</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          {result.weather_alert && (
            <div style={{
              background: '#FFF3CD',
              border: '2px solid #FFC107',
              borderRadius: '8px',
              padding: '1rem',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <AlertTriangle size={24} color="#856404" />
              <div>
                <strong>Weather Alert:</strong> Heavy rainfall expected. Route optimized to avoid vulnerable roads.
              </div>
            </div>
          )}

          <div className="result-section">
            <h3>Route Information</h3>
            <div className="result-item">
              <span className="result-label">From:</span>
              <span className="result-value">{result.start_point}</span>
            </div>
            <div className="result-item">
              <span className="result-label">To:</span>
              <span className="result-value">{result.end_point}</span>
            </div>
            <div className="result-item">
              <span className="result-label">Distance:</span>
              <span className="result-value">{result.distance_km.toFixed(1)} km</span>
            </div>
            <div className="result-item">
              <span className="result-label">Estimated Time:</span>
              <span className="result-value">
                {Math.floor(result.estimated_time_minutes / 60)}h {Math.round(result.estimated_time_minutes % 60)}m
              </span>
            </div>
          </div>

          <div className="result-section">
            <h3>Weather Forecast</h3>
            <div className="result-item">
              <span className="result-label">Expected Rainfall (7 days):</span>
              <span className="result-value">{result.rainfall_forecast.toFixed(1)} mm</span>
            </div>
            <div className="result-item">
              <span className="result-label">Vulnerable Roads Avoided:</span>
              <span className="result-value">{result.vulnerable_roads_avoided}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
