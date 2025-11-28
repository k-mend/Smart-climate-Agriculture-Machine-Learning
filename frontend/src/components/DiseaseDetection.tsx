import { useState } from 'react';
import { Camera, Upload } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface DiseaseResult {
  diagnosis: string;
  confidence: string;
  severity: string;
  treatment_recommendations: string[];
  management_strategy: string[];
  full_analysis?: string;
}

export default function DiseaseDetection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [cropType, setCropType] = useState('');
  const [location, setLocation] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<DiseaseResult | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      if (cropType) formData.append('crop_type', cropType);
      if (location) formData.append('location', location);
      if (symptoms) formData.append('additional_symptoms', symptoms);

      const response = await axios.post(
        `${API_BASE_URL}/api/crop-disease-detection`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Crop Disease Detection</h2>
        <p>Upload a photo of your crop for AI-powered disease diagnosis</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Upload Plant Image</label>
          <div className="file-input-wrapper">
            <input
              type="file"
              id="imageFile"
              className="file-input"
              accept="image/*"
              onChange={handleFileChange}
              required
            />
            <label htmlFor="imageFile" className="file-input-label">
              <Camera size={24} />
              <span>{selectedFile ? selectedFile.name : 'Click to upload image'}</span>
            </label>
          </div>
        </div>

        {previewUrl && (
          <div className="image-preview">
            <img src={previewUrl} alt="Plant preview" />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="cropType">Crop Type (Optional)</label>
          <input
            id="cropType"
            type="text"
            placeholder="e.g., Tomato, Maize, Coffee"
            value={cropType}
            onChange={(e) => setCropType(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="location">Location (Optional)</label>
          <input
            id="location"
            type="text"
            placeholder="e.g., Central Kenya"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="symptoms">Additional Symptoms (Optional)</label>
          <textarea
            id="symptoms"
            placeholder="Describe any other symptoms you've observed..."
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            style={{ minHeight: '80px' }}
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <Upload size={20} />
          {loading ? 'Analyzing Image...' : 'Detect Disease'}
        </button>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI is analyzing your plant image...</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <div className="result-section" style={{
            background: result.severity === 'Severe' ? '#FFEBEE' :
                       result.severity === 'Moderate' ? '#FFF3E0' : '#E8F5E9',
            borderLeft: `4px solid ${
              result.severity === 'Severe' ? '#C62828' :
              result.severity === 'Moderate' ? '#F57C00' : '#4A7C59'
            }`
          }}>
            <h3>Diagnosis</h3>
            <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              {result.diagnosis}
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <div style={{
                padding: '0.5rem 1rem',
                background: 'white',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}>
                <strong>Confidence:</strong> {result.confidence}
              </div>
              <div style={{
                padding: '0.5rem 1rem',
                background: 'white',
                borderRadius: '6px',
                fontSize: '0.875rem'
              }}>
                <strong>Severity:</strong> {result.severity}
              </div>
            </div>
          </div>

          {result.treatment_recommendations.length > 0 && (
            <div className="result-section">
              <h3>Treatment Recommendations</h3>
              {result.treatment_recommendations.map((treatment, index) => (
                <div key={index} className="result-item">
                  {treatment}
                </div>
              ))}
            </div>
          )}

          {result.management_strategy.length > 0 && (
            <div className="result-section">
              <h3>Management Strategy</h3>
              {result.management_strategy.map((strategy, index) => (
                <div key={index} className="result-item">
                  {strategy}
                </div>
              ))}
            </div>
          )}

          {result.full_analysis && (
            <div className="result-section">
              <h3>Full Analysis</h3>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {result.full_analysis}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
