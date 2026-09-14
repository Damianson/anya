import React, { useState, useEffect, useCallback } from 'react';
import RoleToggle from './components/RoleToggle';
import ReportForm from './components/ReportForm';
import IncidentList from './components/IncidentList';
import IncidentDetail from './components/IncidentDetail';
import ResponderView from './components/ResponderView';
import './App.css';

const API_BASE = 'http://127.0.0.1:5000';

export default function App() {
  const [role, setRole] = useState('resident');
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  const fetchIncidents = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch(`${API_BASE}/incidents`);
      if (!res.ok) {
        throw new Error(`Failed to load incidents (Status: ${res.status})`);
      }
      const data = await res.json();
      setIncidents(data);
    } catch (err) {
      console.error('Error fetching incidents:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  function handleReportSubmitted() {
    fetchIncidents();
  }

  function handleSelectIncident(id) {
    setSelectedIncidentId(id);
  }

  function handleCloseDetail() {
    setSelectedIncidentId(null);
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-branding">
          <h1>Anya</h1>
          <p className="header-tagline">Crisis Coordination Platform</p>
        </div>
        <RoleToggle currentRole={role} onRoleChange={setRole} />
      </header>

      <main className="dashboard-main">
        {selectedIncidentId ? (
          <IncidentDetail
            incidentId={selectedIncidentId}
            onClose={handleCloseDetail}
          />
        ) : role === 'responder' ? (
          <ResponderView
            incidents={incidents}
            onRefresh={fetchIncidents}
            onSelectIncident={handleSelectIncident}
          />
        ) : (
          <div className="dashboard-grid">
            <div className="dashboard-column form-column">
              <ReportForm role={role} onSubmitSuccess={handleReportSubmitted} />
            </div>

            <div className="dashboard-column feed-column">
              <IncidentList
                incidents={incidents}
                loading={loading}
                error={error}
                selectedIncidentId={selectedIncidentId}
                onSelectIncident={handleSelectIncident}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
