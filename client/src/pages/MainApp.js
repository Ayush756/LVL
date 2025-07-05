import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // <-- 1. Import
import './MainApp.css';
import Dashboard from '../components/Dashboard';
import MapComponent from '../components/MapComponent';

function MainApp() {
  const [clickedCoords, setClickedCoords] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const navigate = useNavigate(); // <-- 2. Initialize navigate

  const handleMapClick = (coords) => {
    setClickedCoords(coords);
    setStatusMessage('Sending coordinates to backend...');

    fetch('/api/location', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat: coords.lat, lng: coords.lng }),
    })
      .then(response => response.json())
      .then(data => {
        setStatusMessage(data.message || 'Received valid response.');
      })
      .catch(error => {
        setStatusMessage('Error: Could not contact backend.');
      });
  };

  // --- 3. NEW NAVIGATION FUNCTION ---
  const handleGenerateReport = () => {
    if (clickedCoords) {
      // Navigate to the /report page and pass the coordinates in the state
      navigate('/report', { state: { coords: clickedCoords } });
    }
  };

  return (
    <div className="app-container">
      <Dashboard 
        clickedCoords={clickedCoords} 
        statusMessage={statusMessage}
        onGenerateReport={handleGenerateReport} // <-- 4. Pass the function
      />
      <MapComponent 
        onMapClick={handleMapClick} 
        clickedCoords={clickedCoords} 
      />
    </div>
  );
}

export default MainApp;