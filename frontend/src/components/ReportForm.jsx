import React, { useState } from 'react';
import { API_BASE } from '../config';

export default function ReportForm({ role, onSubmitSuccess, t = (k) => k }) {
  const [rawText, setRawText] = useState('');
  const [locationText, setLocationText] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!rawText.trim()) {
      setError('Please provide report details.');
      return;
    }

    setSubmitting(true);
    setError(null);
    setFeedback(null);

    try {
      const payload = {
        raw_text: rawText.trim(),
        reporter_label: role,
        location_text: locationText.trim() || undefined,
        image_url: imageUrl.trim() || undefined,
      };

      const res = await fetch(`${API_BASE}/reports`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || `Server responded with status ${res.status}`);
      }

      // Success
      setFeedback({
        message: t('alert_success') || 'Report submitted successfully!',
        incident: data.incident,
        ai: data.ai,
      });

      // Clear form inputs
      setRawText('');
      setLocationText('');
      setImageUrl('');

      // Notify parent to refresh the incident list
      if (onSubmitSuccess) {
        onSubmitSuccess();
      }
    } catch (err) {
      console.error('Failed to submit report:', err);
      setError(err.message || 'Network error occurred while submitting report.');
    } finally {
      setSubmitting(false);
    }
  }

  const roleDisplay = role === 'responder' ? (t('role_responder') || 'First Responder') : (t('role_resident') || 'Resident');

  return (
    <section className="form-card">
      <h2>{t('form_title')}</h2>
      <p className="form-subtitle">
        {t('form_subtitle')} <strong>{roleDisplay}</strong>
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      {feedback && (
        <div className="alert alert-success">
          <p><strong>{feedback.message}</strong></p>
          {feedback.ai && (
            <div className="ai-feedback-box">
              <p>
                <strong>{t('ai_decision_label')}</strong>{' '}
                {feedback.ai.match_decision === 'MATCH' ? (
                  <span className="badge badge-match">
                    {t('badge_matched')} {feedback.ai.matched_incident_id}
                  </span>
                ) : (
                  <span className="badge badge-new">{t('badge_new')}</span>
                )}
              </p>
              {feedback.ai.has_contradiction && (
                <p className="conflict-alert">
                  <strong>{t('conflict_detected')}</strong> {feedback.ai.contradiction_reason}
                </p>
              )}
              {feedback.ai.reasoning_snippet && (
                <div className="ai-rationale-live">
                  <p className="ai-rationale-live-text">
                    <strong>🤖 {t('ai_rationale_label')}:</strong> {feedback.ai.reasoning_snippet}
                    {feedback.ai.confidence_score !== null && feedback.ai.confidence_score !== undefined && (
                      <span className="confidence-pill">
                        {Math.round(feedback.ai.confidence_score * 100)}% {t('ai_confidence')}
                      </span>
                    )}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="rawText">
            {t('field_desc')} <span className="required">*</span>
          </label>
          <textarea
            id="rawText"
            rows="4"
            placeholder={t('field_desc_placeholder')}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="locationText">{t('field_location')}</label>
          <input
            id="locationText"
            type="text"
            placeholder={t('field_location_placeholder')}
            value={locationText}
            onChange={(e) => setLocationText(e.target.value)}
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="imageUrl">{t('field_image')}</label>
          <input
            id="imageUrl"
            type="url"
            placeholder={t('field_image_placeholder')}
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            disabled={submitting}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={submitting}>
          {submitting ? t('btn_submitting') : t('btn_submit')}
        </button>
      </form>
    </section>
  );
}
