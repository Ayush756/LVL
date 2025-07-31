import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const { coords, userInputs } = location.state || {};

  useEffect(() => {
    if (!coords || !userInputs) {
      setIsLoading(false);
      setError("No location or user input data provided. Please go back.");
      return;
    }

    fetch('/api/generate_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coords, userInputs })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to generate report from server.');
      return res.json();
    })
    .then(data => {
      setReportData(data);
      setIsLoading(false);
    })
    .catch(err => {
      console.error("Error fetching report:", err);
      setError(err.message);
      setIsLoading(false);
    });
  }, [coords, userInputs]);

  const handleDownload = () => alert('Download feature is a work in progress!');
  const handleGoBack = () => navigate('/app');

  // --- THIS IS THE CORRECTED RENDER LOGIC ---

  // First, handle the loading state
  if (isLoading) {
    return (
      <div className="report-page-background">
        <div className="report-container">
          <h2><i className="fa-solid fa-spinner fa-spin"></i> Generating Your Report...</h2>
        </div>
      </div>
    );
  }

  // Second, handle any error state
  if (error) {
    return (
      <div className="report-page-background">
        <div className="report-container">
          <h2><i className="fa-solid fa-triangle-exclamation"></i> An Error Occurred</h2>
          <p>{error}</p>
          <div className="report-actions">
            <button onClick={handleGoBack} className="report-action-button back-button"><i className="fa-solid fa-arrow-left"></i> Go Back</button>
          </div>
        </div>
      </div>
    );
  }

  // Finally, if not loading and no error, it is safe to render the report
  // We add one more check to be absolutely sure reportData exists.
  if (!reportData) {
    return (
      <div className="report-page-background">
        <div className="report-container">
          <h2><i className="fa-solid fa-triangle-exclamation"></i> No Data</h2>
          <p>Report data could not be loaded.</p>
           <div className="report-actions">
            <button onClick={handleGoBack} className="report-action-button back-button"><i className="fa-solid fa-arrow-left"></i> Go Back</button>
          </div>
        </div>
      </div>
    );
  }

  // This code will only be reached if isLoading is false, error is null, AND reportData is not null.
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
            <h4>Population Influenced</h4>
            <p>{reportData.population_analysis.influenced_population_5x5.toLocaleString()}</p>
            <small>(5x5 Grid Area)</small>
          </div>
          <div className="stat-card">
            <h4>Population at Closest Point</h4>
            <p>{reportData.population_analysis.closest_point_population.toLocaleString()}</p>
          </div>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-compass"></i> Competitive & Location Factors</h2>
          <div className="stat-card">
            <h4>Your Attractiveness Score</h4>
            <p>{reportData.competitive_analysis.user_attractiveness}</p>
            <small>Based on your inputs</small>
          </div>
          <div className="stat-card">
            <h4>No. of Competitors</h4>
            <p>{reportData.competitive_analysis.competitor_count}</p>
            <small>(Within a 1km radius)</small>
          </div>
          <div className="stat-card">
            <h4>Distance Score</h4>
            <p>{reportData.distance_score}</p>
            <small>(Lower is better)</small>
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