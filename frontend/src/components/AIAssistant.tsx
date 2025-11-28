import { useState } from 'react';
import { Send } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface AIResponse {
  question: string;
  answer: string;
  confidence_score: number;
  recommendations: string[];
}

export default function AIAssistant() {
  const [question, setQuestion] = useState('');
  const [location, setLocation] = useState('');
  const [cropType, setCropType] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<AIResponse | null>(null);

  const exampleQuestions = [
    'How do I control aphids on tomatoes naturally?',
    'When should I plant maize in Central Kenya?',
    'What are the best organic fertilizers for vegetables?',
    'How to improve clay soil for farming?',
    'Signs of bacterial wilt in tomatoes?'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/agribricks-ai`, {
        question,
        location: location || undefined,
        crop_type: cropType || undefined,
        language: 'en'
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get AI response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuestion: string) => {
    setQuestion(exampleQuestion);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>AI Agricultural Assistant</h2>
        <p>Ask me anything about farming, crops, pests, soil, or weather</p>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <p style={{ fontWeight: 500, marginBottom: '0.5rem', fontSize: '0.9rem' }}>Example Questions:</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {exampleQuestions.map((q, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleExampleClick(q)}
              style={{
                padding: '0.5rem 0.75rem',
                fontSize: '0.875rem',
                border: '1px solid var(--border)',
                borderRadius: '6px',
                background: 'white',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--light-green)';
                e.currentTarget.style.borderColor = 'var(--leaf-green)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'white';
                e.currentTarget.style.borderColor = 'var(--border)';
              }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="question">Your Question</label>
          <textarea
            id="question"
            placeholder="Ask your agricultural question here..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
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
            <label htmlFor="cropType">Crop Type (Optional)</label>
            <input
              id="cropType"
              type="text"
              placeholder="e.g., Tomatoes"
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
            />
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <Send size={20} />
          {loading ? 'Getting Answer...' : 'Ask AI'}
        </button>
      </form>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>AI is thinking...</p>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <div className="result-section" style={{ background: '#E8F5E9' }}>
            <h3>AI Answer</h3>
            <div style={{
              whiteSpace: 'pre-wrap',
              lineHeight: '1.6',
              color: 'var(--text-dark)'
            }}>
              {result.answer}
            </div>
            <div style={{
              marginTop: '1rem',
              padding: '0.5rem',
              background: 'white',
              borderRadius: '6px',
              fontSize: '0.875rem'
            }}>
              <strong>Confidence:</strong> {(result.confidence_score * 100).toFixed(0)}%
            </div>
          </div>

          {result.recommendations.length > 0 && (
            <div className="result-section">
              <h3>Key Recommendations</h3>
              {result.recommendations.map((rec, index) => (
                <div key={index} className="result-item">
                  {rec}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
