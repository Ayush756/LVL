import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Radar } from 'react-chartjs-2';
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js';
import './ReportPage.css';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

function ReportPage() {
    const location = useLocation();
    const navigate = useNavigate();
    
    const [reportData, setReportData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const { coords, userInputs } = location.state || {};

    useEffect(() => {
        if (!coords || !userInputs) {
            setIsLoading(false); setError("No location data provided."); return;
        }
        fetch('/api/generate_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ coords, userInputs })
        })
        .then(res => res.ok ? res.json() : Promise.reject('Failed to generate report.'))
        .then(data => { setReportData(data); setIsLoading(false); })
        .catch(err => { setError(err.toString()); setIsLoading(false); });
    }, [coords, userInputs]);

    const handleGoBack = () => navigate('/app');
    
    // --- RENDER LOGIC ---
    if (isLoading) { /* ... same loading JSX as before ... */ }
    if (error) { /* ... same error JSX as before ... */ }
    if (!reportData) return null;

    const chartData = {
        labels: reportData.factors.labels,
        datasets: [{
            label: 'Viability Score Breakdown',
            data: reportData.factors.scores,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
        }],
    };
    const chartOptions = {
        scales: { r: { suggestedMin: 0, suggestedMax: 100, pointLabels: { font: { size: 12 } } } },
        plugins: { legend: { display: false } },
    };

    return (
        <div className="report-page-background">
            <div className="report-container">
                <div className="report-header">
                    <h1>Business Viability Analysis Report</h1>
                    <p>Generated for location: {coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}</p>
                </div>

                <div className="report-section-grid">
                    <div className="main-score-card">
                        <h3>Overall Viability Score</h3>
                        <div className="final-score-circle">
                            <span className="final-score-value">{reportData.final_score}</span>
                        </div>
                        <p className="score-interpretation">This score represents the weighted average of all analyzed factors. A higher score indicates a more favorable business environment.</p>
                    </div>
                    <div className="chart-card">
                        <h3>Factor Analysis</h3>
                        <Radar data={chartData} options={chartOptions} />
                    </div>
                </div>

                <div className="report-section">
                    <h3>Detailed Breakdown</h3>
                    <div className="details-grid-four-cols">
                        <div className="detail-card">
                            <h4><i className="fa-solid fa-users"></i> Demographic Fit</h4>
                            <p className="detail-value">{reportData.factors.scores[0]}</p>
                            <p className="detail-label">Score (0-100)</p>
                            <p className="detail-explanation">Measures local population size relative to the area's density. Higher is better.</p>
                        </div>
                        <div className="detail-card">
                            <h4><i className="fa-solid fa-signs-post"></i> Landmark Proximity</h4>
                            <p className="detail-value">{reportData.factors.scores[1]}</p>
                            <p className="detail-label">Score (0-100)</p>
                            <p className="detail-explanation">Based on weighted road distance to 6 key landmarks. Higher means closer.</p>
                        </div>
                        <div className="detail-card">
                            <h4><i className="fa-solid fa-chart-pie"></i> Market Share</h4>
                            <p className="detail-value">{reportData.factors.scores[2]}</p>
                            <p className="detail-label">Score (0-100)</p>
                            <p className="detail-explanation">An estimate of your potential market capture based on attractiveness vs. competitors.</p>
                        </div>
                        <div className="detail-card">
                            <h4><i className="fa-solid fa-road"></i> Road Accessibility</h4>
                            <p className="detail-value">{reportData.factors.scores[3]}</p>
                            <p className="detail-label">Score (0-100)</p>
                            <p className="detail-explanation">Measures how close the location is to the road network. Higher is better.</p>
                        </div>
                    </div>
                </div>
                
                <div className="report-actions">
                    <button onClick={handleGoBack} className="report-action-button back-button"><i className="fa-solid fa-arrow-left"></i> New Analysis</button>
                </div>
            </div>
        </div>
    );
}
export default ReportPage;