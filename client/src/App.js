import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import MapComponent from './components/MapComponent';

function App() {
  const [clickedCoords, setClickedCoords] = useState(null);

  const handleMapClick = (coords) => {
    console.log("Map clicked at:", coords);
    setClickedCoords(coords);

    fetch('/api/location', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lat: coords.lat, lng: coords.lng }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Backend response:', data);
      })
      .catch(error => {
        console.error('Error sending data to backend:', error);
      });
  };

  return (
    <div className="app-container">
      <Dashboard clickedCoords={clickedCoords} />
      <MapComponent onMapClick={handleMapClick} />
    </div>
  );
}

export default App;