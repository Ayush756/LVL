import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import MainApp from './pages/MainApp';
import ReportPage from './pages/ReportPage';
function App() {
  return (
    // This <BrowserRouter> component enables the routing system
    <BrowserRouter>
      {/* The <Routes> component holds all our individual URL rules */}
      <Routes>
        {/* Rule 1: If the URL path is "/", show the LandingPage component. */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Rule 2: If the URL path is "/app", show the MainApp component. */}
        <Route path="/app" element={<MainApp />} />
        <Route path="/report" element={<ReportPage />} /> {/* <-- 2. Add Route */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;