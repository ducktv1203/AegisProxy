import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/logs" element={<div className="glass-panel" style={{padding: '2rem'}}><h3>Live Logs (Coming Soon)</h3></div>} />
          <Route path="/rules" element={<div className="glass-panel" style={{padding: '2rem'}}><h3>Security Rules (Coming Soon)</h3></div>} />
          <Route path="/config" element={<div className="glass-panel" style={{padding: '2rem'}}><h3>Configuration (Coming Soon)</h3></div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
