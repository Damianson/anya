import React, { useState } from 'react';

const API_BASE = 'http://127.0.0.1:5000';

export default function ReportForm({ role, onSubmitSuccess }) {
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
        message: 'Report submitted successfully!',
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

  return (
    <section className="form-card">
      <h2>Submit Crisis Report</h2>
      <p className="form-subtitle">
        Reporting as: <strong>{role === 'responder' ? 'First Responder' : 'Resident'}</strong>
      </p>

      {error && <div className="alert alert-error">{error}</div>}

      {feedback && (
        <div className="alert alert-success">
          <p><strong>{feedback.message}</strong></p>
          {feedback.ai && (
            <div className="ai-feedback-box">
              <p>
                <strong>AI Decision:</strong>{' '}
                {feedback.ai.match_decision === 'MATCH' ? (
                  <span className="badge badge-match">
                    Matched Incident #{feedback.ai.matched_incident_id}
                  </span>
                ) : (
                  <span className="badge badge-new">New Incident Created</span>
                )}
              </p>
              {feedback.ai.has_contradiction && (
                <p className="conflict-alert">
                  <strong>Conflict Detected:</strong> {feedback.ai.contradiction_reason}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="rawText">
            Report Description <span className="required">*</span>
          </label>
          <textarea
            id="rawText"
            rows="4"
            placeholder="Describe the situation, hazards, or immediate needs..."
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            disabled={submitting}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="locationText">Location / Landmark (optional)</label>
          <input
            id="locationText"
            type="text"
            placeholder="e.g. Elm St and 4th Ave"
            value={locationText}
            onChange={(e) => setLocationText(e.target.value)}
            disabled={submitting}
          />
        </div>

        <div className="form-group">
          <label htmlFor="imageUrl">Image URL (optional)</label>
          <input
            id="imageUrl"
            type="url"
            placeholder="https://example.com/photo.jpg"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            disabled={submitting}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={submitting}>
          {submitting ? 'Analyzing & Submitting...' : 'Submit Report'}
        </button>
      </form>
    </section>
  );
}
