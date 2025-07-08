import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import backgroundImage from '../assets/background_map.jpg'; 

function LandingPage() {
  const navigate = useNavigate();

  const handleButtonClick = () => {
    navigate('/app'); // Navigate to the main application page
  };

  return (
    <div className="landing-container"
      style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className="landing-content">
        <h1 className="landing-title">LocalVentureLens</h1>
        <p className="landing-subtitle">
          Analyze business viability.
        </p>
        <button className="test-button" onClick={handleButtonClick}>
          Take The Test
        </button>
      </div>
    </div>
  );
}

export default LandingPage;