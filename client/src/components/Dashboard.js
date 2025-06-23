import React from 'react';

function Dashboard({ clickedCoords }) {
  return (
    <div className="dashboard">
      <h1>LocalVentureLens</h1>
      <div className="info-box">
        <h3>Selected Location</h3>
        {clickedCoords ? (
          <div>
            <p><strong>Latitude:</strong> {clickedCoords.lat.toFixed(6)}</p>
            <p><strong>Longitude:</strong> {clickedCoords.lng.toFixed(6)}</p>
          </div>
        ) : (
          <p>Click on the map to select a location.</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;