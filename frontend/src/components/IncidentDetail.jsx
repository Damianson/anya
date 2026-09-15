import React, { useEffect, useState } from 'react';

const API_BASE = 'http://127.0.0.1:5000';

export default function IncidentDetail({ incidentId, onClose, t = (k) => k }) {
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!incidentId) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    async function fetchDetail() {
      try {
        const res = await fetch(`${API_BASE}/incidents/${incidentId}`);
        if (!res.ok) {
          throw new Error(`Incident not found (Status: ${res.status})`);
        }
        const data = await res.json();
        if (isMounted) {
          setIncident(data);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchDetail();

    return () => {
      isMounted = false;
    };
  }, [incidentId]);

  if (!incidentId) return null;

  return (
    <section className="detail-card">
      <div className="detail-header">
        <div>
          <h2>#{incidentId} {t('detail_heading')}</h2>
        </div>
        <button type="button" className="close-btn" onClick={onClose}>
          {t('detail_close')}
        </button>
      </div>

      {loading && <p>Loading details...</p>}
      {error && <div className="alert alert-error">{error}</div>}

      {incident && (
        <div className="detail-content">
          <div className="detail-meta-box">
            <h3>{incident.title}</h3>
            <div className="pills-row">
              <span className={`urgency-pill urgency-${incident.urgency}`}>
                {t(`urgency_${incident.urgency}`) || incident.urgency}
              </span>
              <span className={`state-pill state-${incident.verification_state}`}>
                {t(`state_${incident.verification_state}`) || incident.verification_state}
              </span>
              <span className="type-pill">{t('meta_type')} {incident.type}</span>
            </div>

            <p><strong>{t('meta_location')}</strong> {incident.location_text}</p>
            {incident.people_affected_estimate && (
              <p><strong>{t('meta_affected')}</strong> ~{incident.people_affected_estimate}</p>
            )}
            <p><strong>{t('detail_first_reported')}</strong> {new Date(incident.created_at).toLocaleString()}</p>
            <p><strong>{t('detail_last_updated')}</strong> {new Date(incident.updated_at).toLocaleString()}</p>
          </div>

          <div className="linked-reports-section">
            <h4>{t('detail_linked_reports')} ({incident.reports ? incident.reports.length : 0})</h4>
            {(!incident.reports || incident.reports.length === 0) ? (
              <p className="empty-state">{t('detail_no_reports')}</p>
            ) : (
              <div className="reports-list">
                {incident.reports.map((report) => (
                  <div key={report.id} className="report-item">
                    <div className="report-item-header">
                      <span className="reporter-tag">Report #{report.id} ({report.reporter_label})</span>
                      <span className="report-time">
                        {new Date(report.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="report-text">{report.raw_text}</p>
                    {report.image_url && (
                      <div className="report-image-preview">
                        <img
                          src={report.image_url}
                          alt={`Report #${report.id} attachment`}
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
