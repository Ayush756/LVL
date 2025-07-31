import React, { useState } from 'react'; 
import { useNavigate } from 'react-router-dom';
import './MainApp.css';
import Dashboard from '../components/Dashboard';
import MapComponent from '../components/MapComponent';

function MainApp() {
  const [clickedCoords, setClickedCoords] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const navigate = useNavigate();

  // --- NEW: State to manage user's business parameters ---
  const [userInputs, setUserInputs] = useState({
    cost: 300,
    variety: 25,
    capacity: 40
  });

  const handleMapClick = (coords) => {
    setClickedCoords(coords);
    setStatusMessage('Location selected. Enter your parameters.');
    // Removed the old fetch('/api/location') as it's no longer needed here
  };

  // --- NEW: Function to update state when user types in an input box ---
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    // We use parseInt to make sure we are storing numbers, not strings
    setUserInputs(prevInputs => ({
      ...prevInputs,
      [name]: parseInt(value, 10) || 0
    }));
  };

  // --- MODIFIED: Pass userInputs along with coordinates ---
  const handleGenerateReport = () => {
    if (clickedCoords) {
      // Pass BOTH the coordinates and the user's inputs to the report page
      navigate('/report', { state: { coords: clickedCoords, userInputs: userInputs } });
    }
  };

  return (
    <div className="app-container">
      <Dashboard 
        clickedCoords={clickedCoords} 
        statusMessage={statusMessage}
        onGenerateReport={handleGenerateReport}
        // --- NEW PROPS passed to Dashboard ---
        userInputs={userInputs}
        onInputChange={handleInputChange}
      />
      <MapComponent 
        onMapClick={handleMapClick} 
        clickedCoords={clickedCoords} 
      />
    </div>
  );
}

export default MainApp;