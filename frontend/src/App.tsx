import { useState } from 'react';
import { Sprout, MapPin, Navigation, Bot, Camera } from 'lucide-react';
import LocationAnalysis from './components/LocationAnalysis';
import CropAnalysis from './components/CropAnalysis';
import SmartRoute from './components/SmartRoute';
import AIAssistant from './components/AIAssistant';
import DiseaseDetection from './components/DiseaseDetection';
import './App.css';

type Tab = 'location' | 'crop' | 'route' | 'ai' | 'disease';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('location');

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Sprout className="logo-icon" />
            <div>
              <h1>AgriBricks</h1>
              <p>Smart Climate Agriculture</p>
            </div>
          </div>
        </div>
      </header>

      <nav className="nav">
        <button
          className={`nav-btn ${activeTab === 'location' ? 'active' : ''}`}
          onClick={() => setActiveTab('location')}
        >
          <MapPin size={20} />
          <span>Location Analysis</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'crop' ? 'active' : ''}`}
          onClick={() => setActiveTab('crop')}
        >
          <Sprout size={20} />
          <span>Crop Analysis</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'route' ? 'active' : ''}`}
          onClick={() => setActiveTab('route')}
        >
          <Navigation size={20} />
          <span>Smart Route</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          <Bot size={20} />
          <span>AI Assistant</span>
        </button>
        <button
          className={`nav-btn ${activeTab === 'disease' ? 'active' : ''}`}
          onClick={() => setActiveTab('disease')}
        >
          <Camera size={20} />
          <span>Disease Detection</span>
        </button>
      </nav>

      <main className="main">
        {activeTab === 'location' && <LocationAnalysis />}
        {activeTab === 'crop' && <CropAnalysis />}
        {activeTab === 'route' && <SmartRoute />}
        {activeTab === 'ai' && <AIAssistant />}
        {activeTab === 'disease' && <DiseaseDetection />}
      </main>

      <footer className="footer">
        <p>Powered by Machine Learning & NASA Weather Data</p>
      </footer>
    </div>
  );
}

export default App;
