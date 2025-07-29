import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [proximityData, setProximityData] = useState(null);
  const [populationData, setPopulationData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const { coords } = location.state || { coords: null };

  useEffect(() => {
    if (!coords) {
      setIsLoading(false);
      setError("No location data provided. Please go back and select a location on the map.");
      return;
    }

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
      setProximityData(proximityResult);
      setPopulationData(populationResult);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching analysis data:", err);
      setError(err.message);
      setIsLoading(false);
    });
  }, [coords]);

  const handleDownload = () => alert('Download feature coming soon!');
  const handleGoBack = () => navigate('/app');

  if (isLoading) {
    return <div className="report-page-background"><div className="report-container"><h2><i className="fa-solid fa-spinner fa-spin"></i> Generating Report...</h2></div></div>;
  }

  if (error) {
    return <div className="report-page-background"><div className="report-container"><h2><i className="fa-solid fa-triangle-exclamation"></i> Error</h2><p>{error}</p><div className="report-actions"><button onClick={handleGoBack} className="report-action-button back-button"><i className="fa-solid fa-arrow-left"></i> Go Back</button></div></div></div>;
  }

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

        {/* --- MODIFIED PROXIMITY SECTION --- */}
        <div className="report-section">
          <h2><i className="fa-solid fa-road"></i> Proximity & Accessibility</h2>
          <div className="stat-card">
            <h4>Accessibility Score</h4>
            <p>{proximityData.accessibility_score}</p>
            <small>(Lower is better)</small>
          </div>
          <div className="stat-card">
            <h4>Range of Influence (Max Distance)</h4>
            <p>{proximityData.range_of_influence_km} km</p>
          </div>
        </div>
        
        <div className="report-actions">
          <button onClick={handleGoBack} className="report-action-button back-button"><i className="fa-solid fa-arrow-left"></i> Go Back</button>
          <button onClick={handleDownload} className="report-action-button download-button"><i className="fa-solid fa-download"></i> Download as PDF</button>
        </div>
      </div>
    </div>
  );
}

export default ReportPage;