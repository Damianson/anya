import React, { useState, useEffect, useCallback } from 'react';
import RoleToggle from './components/RoleToggle';
import ReportForm from './components/ReportForm';
import IncidentList from './components/IncidentList';
import IncidentDetail from './components/IncidentDetail';
import ResponderView from './components/ResponderView';
import { TRANSLATIONS } from './translations';
import './App.css';

const API_BASE = 'http://127.0.0.1:5000';

export default function App() {
  const [lang, setLang] = useState('en'); // 'en' | 'pcm'
  const [role, setRole] = useState('resident');
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  // Translation lookup helper
  const t = useCallback(
    (key) => {
      const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
      return dict[key] !== undefined ? dict[key] : (TRANSLATIONS.en[key] || key);
    },
    [lang]
  );

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
          <h1>{t('app_title')}</h1>
          <p className="header-tagline">{t('app_tagline')}</p>
        </div>

        <div className="header-controls">
          <div className="lang-switcher">
            <span className="lang-icon" title="Language Toggle">🌐</span>
            <div className="lang-buttons">
              <button
                type="button"
                className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
                onClick={() => setLang('en')}
              >
                English
              </button>
              <button
                type="button"
                className={`lang-btn ${lang === 'pcm' ? 'active' : ''}`}
                onClick={() => setLang('pcm')}
              >
                Pidgin
              </button>
            </div>
          </div>

          <RoleToggle currentRole={role} onRoleChange={setRole} t={t} />
        </div>
      </header>

      <main className="dashboard-main">
        {selectedIncidentId ? (
          <IncidentDetail
            incidentId={selectedIncidentId}
            onClose={handleCloseDetail}
            t={t}
          />
        ) : role === 'responder' ? (
          <ResponderView
            incidents={incidents}
            onRefresh={fetchIncidents}
            onSelectIncident={handleSelectIncident}
            t={t}
          />
        ) : (
          <div className="dashboard-grid">
            <div className="dashboard-column form-column">
              <ReportForm role={role} onSubmitSuccess={handleReportSubmitted} t={t} />
            </div>

            <div className="dashboard-column feed-column">
              <IncidentList
                incidents={incidents}
                loading={loading}
                error={error}
                selectedIncidentId={selectedIncidentId}
                onSelectIncident={handleSelectIncident}
                t={t}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
