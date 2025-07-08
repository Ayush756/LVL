import React from 'react';

// We now accept 'onGenerateReport' as a prop
function Dashboard({ clickedCoords, statusMessage, onGenerateReport }) {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <i className="fa-solid fa-location-dot"></i>
        <h1>LocalVentureLens</h1>
      </div>

      {/* --- This section is unchanged --- */}
      <div className="info-block">
        <h3>Instructions</h3>
        <p>Click on the map of Nepal to select a location for business viability analysis.</p>
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
      <div className="info-block">
        <h3>Status</h3>
        {statusMessage ? (<p className="status-message success">{statusMessage}</p>) : (<p className="placeholder-text">Waiting for selection...</p>)}
      </div>

      {/* --- NEW BUTTON SECTION --- */}
      <div className="action-block">
        <button 
          className="report-button"
          onClick={onGenerateReport}
          disabled={!clickedCoords} // Button is disabled if no coordinates are selected
        >
          <i className="fa-solid fa-chart-line"></i>
          Generate Report
        </button>
      </div>
    </div>
  );
}

export default Dashboard;