import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

function App() {
  const [showGallery, setShowGallery] = useState(false);

  useEffect(() => {
    // placeholder
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            LumaForge
          </h1>
          <button
            onClick={() => setShowGallery(!showGallery)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            {showGallery ? 'Hide Gallery' : 'Show Gallery'}
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-4">
        <div className="mb-6">
          <MusicVideoUpload />
        </div>
      </div>
    </div>
  );
}

export default App;
