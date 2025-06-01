import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyStatus, setCopyStatus] = useState('idle');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(""); // Clear any previous errors
    setResult(null); // Clear previous results
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setError("");

    try {
      const response = await fetch("https://caption-generator-veku.onrender.com/vibe", 
       {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (error) {
      console.error("Upload failed", error);
      setError("Failed to connect to server. Please try again.");
      setResult(null);
    }

    setLoading(false);
  };
const handleCopyCaption = async () => {
  if (!result?.caption) {
    alert("No caption to copy!");
    return;
  }

  setCopyStatus('copying');

  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(result.caption);
      setCopyStatus('success');
    } 
    else {
      const textArea = document.createElement('textarea');
      textArea.value = result.caption;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      if (!successful) {
        throw new Error('Copy command failed');
      }
      setCopyStatus('success');
    }
  } catch (error) {
    console.error('Failed to copy:', error);
    setCopyStatus('error');
    alert("Failed to copy caption. Please try selecting and copying manually.");
  }

  // Reset status after 2 seconds
  setTimeout(() => setCopyStatus('idle'), 2000);
};

  const handleNewPhoto = () => {
    setFile(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="App">
      <header>
        <h1>🌈 Vibe Sync</h1>
        <p>Detect emotions and get instant captions for your photos!</p>
      </header>

      <div className="upload-section">
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleFileChange}
          style={{ display: 'none' }}
          id="file-input"
        />
        <label htmlFor="file-input" className="file-label">
          📸 Choose Photo
        </label>
        
        <button 
          onClick={handleUpload} 
          disabled={loading || !file}
          className={`upload-btn ${loading ? 'loading' : ''}`}
        >
          {loading ? "🔍 Analyzing..." : "✨ Generate Vibe"}
        </button>
      </div>

      {error && (
        <div className="error">
          <p>⚠️ {error}</p>
        </div>
      )}

      {file && (
        <div className="preview">
          <h3>📷 Preview:</h3>
          <img 
            src={URL.createObjectURL(file)} 
            alt="Preview" 
            style={{ 
              maxWidth: "300px", 
              borderRadius: "12px",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)"
            }} 
          />
        </div>
      )}

      {result && (
        <div className="results">
          <div className="detection-grid">
            <div className="emotion-section">
              <h3>🎭 Detected Emotion</h3>
              <div className="emotion-card">
                <span className="emotion-name">{result.emotion}</span>
                <span className="confidence">
                  {(result.emotion_confidence * 100).toFixed(1)}% confident
                </span>
              </div>
            </div>

            <div className="scene-section">
              <h3>🌟 Detected Scene</h3>
              <div className="scene-card">
                <span className="scene-name">{result.scene}</span>
                <span className="confidence">
                  {(result.scene_confidence * 100).toFixed(1)}% confident
                </span>
              </div>
            </div>
          </div>

          <div className="primary-vibe">
            <p>
              <strong>Primary Vibe:</strong> {result.primary_vibe === 'emotion' ? '🎭 Emotion-based' : '🌟 Scene-based'}
            </p>
          </div>

          <div className="caption-section">
            <h3>📝 Your Caption</h3>
            <div className="caption-card">
              <p className="caption-text">{result.caption}</p>
              <div className="caption-actions">
              <button 
  onClick={handleCopyCaption} 
  className="copy-btn"
  disabled={copyStatus === 'copying'}
>
  {copyStatus === 'copying' ? '📋 Copying...' : 
   copyStatus === 'success' ? '✅ Copied!' : 
   copyStatus === 'error' ? '❌ Try Again' : 
   '📋 Copy Caption'}
</button>
                
              </div>
            </div>
          </div>

          {result.vibe && result.vibe.length > 1 && (
            <div className="all-emotions">
              <h4>🎯 All Detected Emotions:</h4>
              <div className="emotion-list">
                {result.vibe.map((emotion, index) => (
                  <div key={index} className="emotion-item">
                    <span className="emotion-label">{emotion.label}</span>
                    <div className="emotion-bar">
                      <div 
                        className="emotion-fill" 
                        style={{ width: `${emotion.score * 100}%` }}
                      ></div>
                    </div>
                    <span className="emotion-percentage">
                      {(emotion.score * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button onClick={handleNewPhoto} className="new-photo-btn">
            🔄 Try Another Photo
          </button>
        </div>
      )}

      <footer>
        <p>💡 <strong>Note:</strong> Captions are AI-generated suggestions based on detected emotions!</p>
      </footer>
    </div>
  );
}

export default App;