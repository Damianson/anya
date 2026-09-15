import React, { useState } from 'react';
import MapView from './MapView';

export default function IncidentList({
  incidents,
  loading,
  error,
  selectedIncidentId,
  onSelectIncident,
  t = (k) => k,
}) {
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'map'

  if (loading) {
    return <div className="list-card"><p>Loading incidents...</p></div>;
  }

  if (error) {
    return (
      <div className="list-card">
        <div className="alert alert-error">Failed to load incidents: {error}</div>
      </div>
    );
  }

  return (
    <section className="list-card">
      <div className="list-header">
        <h2>{t('list_heading')} ({incidents.length})</h2>
        <div className="view-mode-toggle">
          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            📋 {t('btn_view_list')}
          </button>
          <button
            type="button"
            className={`view-toggle-btn ${viewMode === 'map' ? 'active' : ''}`}
            onClick={() => setViewMode('map')}
          >
            🗺️ {t('btn_view_map')}
          </button>
        </div>
      </div>

      {viewMode === 'map' ? (
        <MapView
          incidents={incidents}
          onSelectIncident={onSelectIncident}
          t={t}
        />
      ) : incidents.length === 0 ? (
        <p className="empty-state">{t('empty_incidents')}</p>
      ) : (
        <div className="incidents-grid">
          {incidents.map((incident) => {
            const isSelected = selectedIncidentId === incident.id;
            const urgencyKey = `urgency_${incident.urgency}`;
            const stateKey = `state_${incident.verification_state}`;

            return (
              <div
                key={incident.id}
                className={`incident-item ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectIncident(incident.id)}
              >
                <div className="incident-top">
                  <span className="incident-id">#{incident.id}</span>
                  <span className={`urgency-pill urgency-${incident.urgency}`}>
                    {t(urgencyKey) || incident.urgency}
                  </span>
                  <span className={`state-pill state-${incident.verification_state}`}>
                    {t(stateKey) || incident.verification_state}
                  </span>
                </div>

                <h3 className="incident-title">{incident.title}</h3>

                <div className="incident-meta">
                  <p><strong>{t('meta_type')}</strong> {incident.type}</p>
                  <p><strong>{t('meta_location')}</strong> {incident.location_text}</p>
                  {incident.people_affected_estimate && (
                    <p><strong>{t('meta_affected')}</strong> ~{incident.people_affected_estimate} people</p>
                  )}
                  <p className="incident-time">
                    {new Date(incident.created_at).toLocaleString()}
                  </p>
                </div>

                {incident.latest_ai_reasoning && (
                  <div className="card-ai-rationale">
                    <div className="card-rationale-header">
                      <span className="rationale-tag">🤖 {t('ai_rationale_label')}</span>
                      {incident.latest_ai_confidence !== null && incident.latest_ai_confidence !== undefined && (
                        <span className="confidence-pill">
                          {Math.round(incident.latest_ai_confidence * 100)}% {t('ai_confidence')}
                        </span>
                      )}
                    </div>
                    <p className="card-rationale-text">{incident.latest_ai_reasoning}</p>
                  </div>
                )}

                <button
                  type="button"
                  className="view-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectIncident(incident.id);
                  }}
                >
                  {isSelected ? t('btn_viewing') : t('btn_view_details')}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
