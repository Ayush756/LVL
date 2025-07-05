import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './ReportPage.css';

function ReportPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get the coordinates passed from the MainApp page
  // We add a fallback in case the user navigates here directly
  const { coords } = location.state || { coords: { lat: 'N/A', lng: 'N/A' } };

  const handleDownload = () => {
    // In a real app, you'd generate a PDF here.
    // For now, we'll just show an alert.
    alert('Downloading report for ' + coords.lat + ', ' + coords.lng);
  };

  const handleGoBack = () => {
    navigate('/app'); // Navigate back to the map
  };

  return (
    <div className="report-page-background">
      <div className="report-container">
        <div className="report-header">
          <h1>Business Viability Report</h1>
          <p>LocationVentureLens Analysis</p>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-map-location-dot"></i> Selected Location</h2>
          <p><strong>Latitude:</strong> {coords.lat.toFixed(6)}</p>
          <p><strong>Longitude:</strong> {coords.lng.toFixed(6)}</p>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-chart-pie"></i> Market Analysis (Placeholder)</h2>
          <p><strong>Demographics:</strong> Young population with moderate income.</p>
          <p><strong>Competition:</strong> Low competition for boutique cafes, high for general stores.</p>
          <p><strong>Foot Traffic:</strong> Estimated 500-700 people per day.</p>
        </div>

        <div className="report-section">
          <h2><i className="fa-solid fa-thumbs-up"></i> Viability Score (Placeholder)</h2>
          <div className="score-box">
            <span>78/100</span>
            <p>Good Potential</p>
          </div>
          <p>This location shows strong potential for a service-based business targeting young adults. Infrastructure and accessibility are rated highly.</p>
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