import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // State to hold our new analysis data
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const { coords } = location.state || { coords: null };

  // --- NEW: Fetch data when the page loads ---
  useEffect(() => {
    if (!coords) {
      // If no coordinates were passed, don't try to fetch
      setIsLoading(false);
      return;
    }

    fetch('/api/analyze_proximity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(coords)
    })
    .then(res => res.json())
    .then(data => {
      setAnalysisData(data);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching analysis:", err);
      setIsLoading(false);
    });
  }, [coords]); // This effect runs only when 'coords' changes

  // ... (keep handleDownload and handleGoBack functions) ...

  if (isLoading) {
    return <div className="report-page-background"><div className="report-container"><h2>Generating Report...</h2></div></div>;
  }

  if (!analysisData) {
    return <div className="report-page-background"><div className="report-container"><h2>Could not generate report. Please go back and select a location.</h2></div></div>;
  }

  return (
    <div className="report-page-background">
      <div className="report-container">
        {/* ... (keep report-header) ... */}
        
        {/* --- NEW: Display the dynamic data --- */}
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
              {analysisData.proximity_analysis.map(item => (
                <tr key={item.name}>
                  <td>{item.name}</td>
                  <td>{item.distance_km}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* ... (you can add other report sections here) ... */}
        {/* ... (keep report-actions) ... */}
      </div>
    </div>
  );
}

export default ReportPage;
