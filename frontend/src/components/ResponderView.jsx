import React, { useState } from 'react';

const API_BASE = 'http://127.0.0.1:5000';

export default function ResponderView({ incidents, onRefresh, onSelectIncident }) {
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [actionError, setActionError] = useState(null);

  // Priority sorting: Disputed and Unverified first, then corroborated, verified, resolved
  const priorityOrder = {
    disputed: 0,
    unverified: 1,
    corroborated: 2,
    verified: 3,
    resolved: 4,
  };

  const sortedIncidents = [...incidents].sort((a, b) => {
    const pA = priorityOrder[a.verification_state] ?? 99;
    const pB = priorityOrder[b.verification_state] ?? 99;
    if (pA !== pB) return pA - pB;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  const needsAttentionCount = incidents.filter(
    (inc) => inc.verification_state === 'disputed' || inc.verification_state === 'unverified'
  ).length;

  async function handleVerify(id) {
    setActionLoadingId(`verify-${id}`);
    setActionError(null);
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}/verify`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to verify incident');
      onRefresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }

  async function handleDispute(id) {
    setActionLoadingId(`dispute-${id}`);
    setActionError(null);
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}/dispute`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to dispute incident');
      onRefresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }

  async function handleGenerateTask(id) {
    setActionLoadingId(`task-${id}`);
    setActionError(null);
    try {
      const res = await fetch(`${API_BASE}/incidents/${id}/tasks/generate`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to generate task');
      onRefresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }

  async function handleClaimTask(taskId) {
    setActionLoadingId(`claim-${taskId}`);
    setActionError(null);
    try {
      const res = await fetch(`${API_BASE}/tasks/${taskId}/claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ claimed_by: 'First Responder' }),
      });
      if (!res.ok) throw new Error('Failed to claim task');
      onRefresh();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActionLoadingId(null);
    }
  }

  return (
    <section className="responder-workspace">
      <div className="responder-header">
        <div>
          <h2>Emergency Responder Triage Board</h2>
          <p className="responder-sub">
            Review field reports, verify or dispute crisis events, and dispatch operational tasks.
          </p>
        </div>
        <button type="button" className="refresh-btn" onClick={onRefresh}>
          ↻ Refresh Triage
        </button>
      </div>

      <div className="triage-metrics">
        <div className="metric-box alert-box">
          <span className="metric-number">{needsAttentionCount}</span>
          <span className="metric-label">Needing Attention (Disputed / Unverified)</span>
        </div>
        <div className="metric-box success-box">
          <span className="metric-number">
            {incidents.filter((i) => i.verification_state === 'verified').length}
          </span>
          <span className="metric-label">Verified Incidents</span>
        </div>
        <div className="metric-box neutral-box">
          <span className="metric-number">{incidents.length}</span>
          <span className="metric-label">Total Tracked</span>
        </div>
      </div>

      {actionError && <div className="alert alert-error">{actionError}</div>}

      {sortedIncidents.length === 0 ? (
        <div className="empty-state">No incidents currently in the database.</div>
      ) : (
        <div className="responder-cards">
          {sortedIncidents.map((incident) => {
            const isVerified = incident.verification_state === 'verified';
            const isDisputed = incident.verification_state === 'disputed';
            const isUnverified = incident.verification_state === 'unverified';

            return (
              <div
                key={incident.id}
                className={`responder-card ${isDisputed ? 'card-disputed' : ''} ${
                  isUnverified ? 'card-unverified' : ''
                }`}
              >
                <div className="responder-card-top">
                  <div className="card-identity">
                    <span className="incident-id">#{incident.id}</span>
                    <span className={`urgency-pill urgency-${incident.urgency}`}>
                      {incident.urgency}
                    </span>
                    <span className={`state-pill state-${incident.verification_state}`}>
                      {incident.verification_state}
                    </span>
                    <span className="type-pill">{incident.type}</span>
                  </div>
                  <div className="card-reports-count">
                    {incident.report_count ?? 1} report(s)
                  </div>
                </div>

                <h3 className="responder-card-title">{incident.title}</h3>

                <div className="responder-card-meta">
                  <p><strong>Location:</strong> {incident.location_text}</p>
                  {incident.people_affected_estimate && (
                    <p><strong>Estimated Affected:</strong> ~{incident.people_affected_estimate} people</p>
                  )}
                  <p className="card-timestamp">
                    Created: {new Date(incident.created_at).toLocaleTimeString()}
                  </p>
                </div>

                {/* Human Verification Actions */}
                <div className="verification-actions">
                  <span className="action-label">Verification Action:</span>
                  <div className="action-buttons-row">
                    <button
                      type="button"
                      className="btn-action btn-verify"
                      disabled={isVerified || actionLoadingId === `verify-${incident.id}`}
                      onClick={() => handleVerify(incident.id)}
                    >
                      {isVerified ? '✓ Verified' : 'Mark Verified'}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-dispute"
                      disabled={isDisputed || actionLoadingId === `dispute-${incident.id}`}
                      onClick={() => handleDispute(incident.id)}
                    >
                      {isDisputed ? '⚠ Disputed' : 'Mark Disputed'}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-suggest-task"
                      disabled={actionLoadingId === `task-${incident.id}`}
                      onClick={() => handleGenerateTask(incident.id)}
                      title={isVerified ? 'Generate action task' : 'Recommended for verified incidents'}
                    >
                      {actionLoadingId === `task-${incident.id}`
                        ? 'Generating...'
                        : '+ Generate Suggested Task'}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-details"
                      onClick={() => onSelectIncident(incident.id)}
                    >
                      Inspect Reports
                    </button>
                  </div>
                </div>

                {/* Associated Tasks Section */}
                <div className="incident-tasks-container">
                  <h4>Operational Tasks ({incident.tasks ? incident.tasks.length : 0})</h4>
                  {(!incident.tasks || incident.tasks.length === 0) ? (
                    <p className="no-tasks-text">No tasks generated yet. Click "Generate Suggested Task" to dispatch response.</p>
                  ) : (
                    <div className="tasks-list">
                      {incident.tasks.map((task) => (
                        <div key={task.id} className="task-row">
                          <div className="task-main">
                            <span className={`task-status-tag status-${task.status}`}>
                              {task.status}
                            </span>
                            <span className="task-desc">{task.description}</span>
                          </div>

                          <div className="task-meta-right">
                            {task.claimed_by && (
                              <span className="claimed-by-tag">Claimed by: {task.claimed_by}</span>
                            )}
                            {task.status === 'open' && (
                              <button
                                type="button"
                                className="claim-btn"
                                disabled={actionLoadingId === `claim-${task.id}`}
                                onClick={() => handleClaimTask(task.id)}
                              >
                                {actionLoadingId === `claim-${task.id}` ? 'Claiming...' : 'Claim Task'}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

