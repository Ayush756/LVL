import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // State for our different analyses
  const [proximityData, setProximityData] = useState(null);
  const [populationData, setPopulationData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get the coordinates passed from the MainApp page
  // We add a fallback in case the user navigates here directly
  const { coords } = location.state || { coords: null };

  // This effect hook runs once when the component loads
  useEffect(() => {
    // If no coordinates were passed (e.g., user navigated directly to /report), don't fetch.
    if (!coords) {
      setIsLoading(false);
      setError("No location data provided. Please go back and select a location on the map.");
      return;
    }

    // Use Promise.all to fetch from both endpoints simultaneously for efficiency
    Promise.all([
      fetch('/api/analyze_proximity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(coords)
      }).then(res => {
        if (!res.ok) throw new Error('Proximity analysis failed');
        return res.json();
      }),

      fetch('/api/analyze_population', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(coords)
      }).then(res => {
        if (!res.ok) throw new Error('Population analysis failed');
        return res.json();
      })
    ])
    .then(([proximityResult, populationResult]) => {
      // Once both fetches are successful, update the state
      setProximityData(proximityResult);
      setPopulationData(populationResult);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching analysis data:", err);
      setError(err.message);
      setIsLoading(false);
    });
  }, [coords]); // The effect depends on 'coords', but will only run once on page load

  const handleDownload = () => {
    alert('Download feature coming soon!');
  };
  
  const handleGoBack = () => {
    navigate('/app'); // Navigate back to the map page
  };

  // --- Render logic based on the state ---

  // 1. Show a loading state while fetching data
  if (isLoading) {
    return (
      <div className="report-page-background">
        <div className="report-container">
          <h2><i className="fa-solid fa-spinner fa-spin"></i> Generating Report...</h2>
          <p>Analyzing location data. Please wait.</p>
        </div>
      </div>
    );
  }

  // 2. Show an error state if something went wrong
  if (error) {
    return (
      <div className="report-page-background">
        <div className="report-container">
          <h2><i className="fa-solid fa-triangle-exclamation"></i> Error</h2>
          <p>{error}</p>
          <div className="report-actions">
            <button onClick={handleGoBack} className="report-action-button back-button">
              <i className="fa-solid fa-arrow-left"></i> Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 3. Show the full report if data is loaded successfully
  return (
    <div className="report-page-background">
      <div className="report-container">
        <div className="report-header">
          <h1>Business Viability Report</h1>
          <p>For location: {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}</p>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-users"></i> Population Analysis</h2>
          <div className="stat-card">
            <h4>Population Influenced (5x5 Grid)</h4>
            <p>{populationData.influenced_population_5x5.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h4>Population at Closest Point</h4>
            <p>{populationData.closest_point_population.toLocaleString()}</p>
          </div>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-road"></i> Proximity to Key Locations</h2>
          <table className="proximity-table">
            <thead>
              <tr>
                <th>Destination</th>
                <th>Road Distance (km)</th>
              </tr>
            </thead>
            <tbody>
              {proximityData.proximity_analysis.map((item, index) => (
                <tr key={index}>
                  <td>{item.name}</td>
                  <td>{item.distance_km}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="report-actions">
          <button onClick={handleGoBack} className="report-action-button back-button">
            <i className="fa-solid fa-arrow-left"></i> Go Back
          </button>
          <button onClick={handleDownload} className="report-action-button download-button">
            <i className="fa-solid fa-download"></i> Download as PDF
          </button>
        </div>
      </div>
    </div>
  );
}

export default ReportPage;