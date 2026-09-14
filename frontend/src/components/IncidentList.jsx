import React from 'react';

export default function IncidentList({
  incidents,
  loading,
  error,
  selectedIncidentId,
  onSelectIncident,
}) {
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
        <h2>Active Incidents ({incidents.length})</h2>
      </div>

      {incidents.length === 0 ? (
        <p className="empty-state">No incidents recorded yet. Submit a report to begin.</p>
      ) : (
        <div className="incidents-grid">
          {incidents.map((incident) => {
            const isSelected = selectedIncidentId === incident.id;
            return (
              <div
                key={incident.id}
                className={`incident-item ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectIncident(incident.id)}
              >
                <div className="incident-top">
                  <span className="incident-id">#{incident.id}</span>
                  <span className={`urgency-pill urgency-${incident.urgency}`}>
                    {incident.urgency}
                  </span>
                  <span className={`state-pill state-${incident.verification_state}`}>
                    {incident.verification_state}
                  </span>
                </div>

                <h3 className="incident-title">{incident.title}</h3>

                <div className="incident-meta">
                  <p><strong>Type:</strong> {incident.type}</p>
                  <p><strong>Location:</strong> {incident.location_text}</p>
                  {incident.people_affected_estimate && (
                    <p><strong>Affected:</strong> ~{incident.people_affected_estimate} people</p>
                  )}
                  <p className="incident-time">
                    {new Date(incident.created_at).toLocaleString()}
                  </p>
                </div>

                <button
                  type="button"
                  className="view-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectIncident(incident.id);
                  }}
                >
                  {isSelected ? 'Viewing' : 'View Details'}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
