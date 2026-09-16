import React, { useState } from 'react';
import { API_BASE } from '../config';

export default function ResponderView({ incidents, onRefresh, onSelectIncident, t = (k) => k }) {
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
          <h2>{t('responder_heading')}</h2>
          <p className="responder-sub">
            {t('responder_sub')}
          </p>
        </div>
        <button type="button" className="refresh-btn" onClick={onRefresh}>
          {t('btn_refresh')}
        </button>
      </div>

      <div className="triage-metrics">
        <div className="metric-box alert-box">
          <span className="metric-number">{needsAttentionCount}</span>
          <span className="metric-label">{t('metric_attention')}</span>
        </div>
        <div className="metric-box success-box">
          <span className="metric-number">
            {incidents.filter((i) => i.verification_state === 'verified').length}
          </span>
          <span className="metric-label">{t('metric_verified')}</span>
        </div>
        <div className="metric-box neutral-box">
          <span className="metric-number">{incidents.length}</span>
          <span className="metric-label">{t('metric_total')}</span>
        </div>
      </div>

      {actionError && <div className="alert alert-error">{actionError}</div>}

      {sortedIncidents.length === 0 ? (
        <div className="empty-state">{t('empty_incidents')}</div>
      ) : (
        <div className="responder-cards">
          {sortedIncidents.map((incident) => {
            const isVerified = incident.verification_state === 'verified';
            const isDisputed = incident.verification_state === 'disputed';
            const isUnverified = incident.verification_state === 'unverified';
            const urgencyKey = `urgency_${incident.urgency}`;
            const stateKey = `state_${incident.verification_state}`;

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
                      {t(urgencyKey) || incident.urgency}
                    </span>
                    <span className={`state-pill state-${incident.verification_state}`}>
                      {t(stateKey) || incident.verification_state}
                    </span>
                    <span className="type-pill">{incident.type}</span>
                  </div>
                  <div className="card-reports-count">
                    {incident.report_count ?? 1} report(s)
                  </div>
                </div>

                <h3 className="responder-card-title">{incident.title}</h3>

                <div className="responder-card-meta">
                  <p><strong>{t('meta_location')}</strong> {incident.location_text}</p>
                  {incident.people_affected_estimate && (
                    <p><strong>{t('meta_affected')}</strong> ~{incident.people_affected_estimate} people</p>
                  )}
                  <p className="card-timestamp">
                    {t('meta_created')} {new Date(incident.created_at).toLocaleTimeString()}
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

                {/* Human Verification Actions */}
                <div className="verification-actions">
                  <span className="action-label">{t('verification_action')}</span>
                  <div className="action-buttons-row">
                    <button
                      type="button"
                      className="btn-action btn-verify"
                      disabled={isVerified || actionLoadingId === `verify-${incident.id}`}
                      onClick={() => handleVerify(incident.id)}
                    >
                      {isVerified ? t('btn_verified') : t('btn_verify')}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-dispute"
                      disabled={isDisputed || actionLoadingId === `dispute-${incident.id}`}
                      onClick={() => handleDispute(incident.id)}
                    >
                      {isDisputed ? t('btn_disputed') : t('btn_dispute')}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-suggest-task"
                      disabled={actionLoadingId === `task-${incident.id}`}
                      onClick={() => handleGenerateTask(incident.id)}
                      title={isVerified ? 'Generate action task' : 'Recommended for verified incidents'}
                    >
                      {actionLoadingId === `task-${incident.id}`
                        ? t('btn_generating')
                        : t('btn_suggest_task')}
                    </button>

                    <button
                      type="button"
                      className="btn-action btn-details"
                      onClick={() => onSelectIncident(incident.id)}
                    >
                      {t('btn_inspect')}
                    </button>
                  </div>
                </div>

                {/* Associated Tasks Section */}
                <div className="incident-tasks-container">
                  <h4>{t('tasks_heading')} ({incident.tasks ? incident.tasks.length : 0})</h4>
                  {(!incident.tasks || incident.tasks.length === 0) ? (
                    <p className="no-tasks-text">{t('no_tasks')}</p>
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
                              <span className="claimed-by-tag">{t('claimed_by_label')} {task.claimed_by}</span>
                            )}
                            {task.status === 'open' && (
                              <button
                                type="button"
                                className="claim-btn"
                                disabled={actionLoadingId === `claim-${task.id}`}
                                onClick={() => handleClaimTask(task.id)}
                              >
                                {actionLoadingId === `claim-${task.id}` ? t('btn_claiming') : t('btn_claim_task')}
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
