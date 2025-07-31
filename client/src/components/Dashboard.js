import React from 'react';

// We now accept 'userInputs' and 'onInputChange' as props
function Dashboard({ clickedCoords, statusMessage, onGenerateReport, userInputs, onInputChange }) {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <i className="fa-solid fa-location-dot"></i>
        <h1>LocalVentureLens</h1>
      </div>

      <div className="info-block">
        <h3>Instructions</h3>
        <p>1. Click a location on the map. <br/> 2. Enter your business details below. <br/> 3. Generate the report.</p>
      </div>

      {/* --- NEW USER INPUT SECTION --- */}
      <div className="info-block">
        <h3>Your Business Parameters</h3>
        <div className="input-group">
          <label htmlFor="cost">Avg. Cost (e.g., NPR 300)</label>
          <input 
            type="number" 
            id="cost" 
            name="cost" 
            value={userInputs.cost} 
            onChange={onInputChange} 
          />
        </div>
        <div className="input-group">
          <label htmlFor="variety">Variety (e.g., 25 menu items)</label>
          <input 
            type="number" 
            id="variety" 
            name="variety" 
            value={userInputs.variety} 
            onChange={onInputChange} 
          />
        </div>
        <div className="input-group">
          <label htmlFor="capacity">Capacity (e.g., 40 seats)</label>
          <input 
            type="number" 
            id="capacity" 
            name="capacity" 
            value={userInputs.capacity} 
            onChange={onInputChange} 
          />
        </div>
      </div>

      <div className="info-block">
        <h3>Selected Coordinates</h3>
        {clickedCoords ? (
          <div>
            <div className="coord-item">
              <i className="fa-solid fa-arrows-left-right"></i>
              <span><strong>Longitude:</strong> {clickedCoords.lng.toFixed(6)}</span>
            </div>
            <div className="coord-item">
              <i className="fa-solid fa-arrows-up-down"></i>
              <span><strong>Latitude:</strong> {clickedCoords.lat.toFixed(6)}</span>
            </div>
          </div>
        ) : (<p className="placeholder-text">No location selected yet.</p>)}
      </div>
      
      <div className="action-block">
        <button 
          className="report-button"
          onClick={onGenerateReport}
          disabled={!clickedCoords}
        >
          <i className="fa-solid fa-chart-line"></i>
          Generate Report
        </button>
      </div>
    </div>
  );
}

export default Dashboard;