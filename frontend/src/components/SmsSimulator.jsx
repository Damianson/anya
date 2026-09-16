import React, { useState } from 'react';
import { API_BASE } from '../config';

const QUICK_SCENARIOS = [
  {
    label: "Ajah Flood Escalation (Pidgin)",
    phone: "+234 803 555 0192",
    text: "Water don reach car window for Ajah bridge! People dey stand on top bus stop roof! Send rescue boat quick!"
  },
  {
    label: "Abuja Live Wire Sparks (English)",
    phone: "+234 802 777 4411",
    text: "Fallen high-tension cable sparking near Banex plaza on Aminu Kano. Road is blocked and people are running."
  },
  {
    label: "Ikeja Pipe Repaired Dispute (English)",
    phone: "+234 814 333 8899",
    text: "Lagos Water Corporation has completely fixed the burst pipe on Isaac John Street. The sidewalk is completely dry."
  }
];

export default function SmsSimulator({ isOpen, onClose, onReportDelivered, t = (k) => k }) {
  const [senderPhone, setSenderPhone] = useState('+234 803 555 0192');
  const [smsBody, setSmsBody] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [conversation, setConversation] = useState(null);

  if (!isOpen) return null;

  async function handleSend(e) {
    if (e) e.preventDefault();
    if (!smsBody.trim()) {
      setError("Please enter or select an SMS message.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const payload = {
        from: senderPhone.trim() || '+234 800 000 0000',
        text: smsBody.trim(),
      };

      const res = await fetch(`${API_BASE}/webhooks/sms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `Gateway returned status ${res.status}`);
      }

      setConversation({
        sentText: smsBody.trim(),
        sender: senderPhone.trim(),
        replyText: data.reply_sms,
        incident: data.incident,
        autoEscalated: data.auto_escalated,
        ai: data.ai,
        timestamp: new Date().toLocaleTimeString(),
      });

      setSmsBody('');

      if (onReportDelivered) {
        onReportDelivered();
      }
    } catch (err) {
      console.error("SMS Gateway error:", err);
      setError(err.message || "Failed to transmit simulated SMS over gateway.");
    } finally {
      setSubmitting(false);
    }
  }

  function applyScenario(scenario) {
    setSenderPhone(scenario.phone);
    setSmsBody(scenario.text);
    setError(null);
  }

  return (
    <div className="sms-modal-backdrop" onClick={onClose}>
      <div className="sms-modal-window" onClick={(e) => e.stopPropagation()}>
        <div className="sms-modal-header">
          <div>
            <div className="sms-channel-badge">📡 {t('sms_badge_2g')}</div>
            <h3>{t('sms_modal_title')}</h3>
            <p className="sms-modal-sub">{t('sms_modal_sub')}</p>
          </div>
          <button type="button" className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="sms-modal-body">
          {error && <div className="alert alert-error">{error}</div>}

          {/* Quick Scenario Picker */}
          <div className="sms-scenarios-section">
            <label className="sms-label">{t('sms_quick_scenarios')}</label>
            <div className="sms-scenarios-row">
              {QUICK_SCENARIOS.map((sc, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="sms-scenario-chip"
                  onClick={() => applyScenario(sc)}
                  disabled={submitting}
                >
                  ⚡ {sc.label}
                </button>
              ))}
            </div>
          </div>

          {/* SMS Compose Form */}
          <form onSubmit={handleSend} className="sms-compose-form">
            <div className="form-group">
              <label htmlFor="smsPhone" className="sms-label">{t('sms_sender_label')}</label>
              <input
                id="smsPhone"
                type="text"
                value={senderPhone}
                onChange={(e) => setSenderPhone(e.target.value)}
                disabled={submitting}
                className="sms-phone-input"
                placeholder="+234 803 000 0000"
              />
            </div>

            <div className="form-group">
              <label htmlFor="smsText" className="sms-label">{t('sms_message_label')}</label>
              <textarea
                id="smsText"
                rows="3"
                value={smsBody}
                onChange={(e) => setSmsBody(e.target.value)}
                disabled={submitting}
                className="sms-text-area"
                placeholder="Type raw SMS report or select a scenario above..."
              />
            </div>

            <button
              type="submit"
              className="submit-btn sms-send-btn"
              disabled={submitting || !smsBody.trim()}
            >
              {submitting ? t('sms_btn_sending') : t('sms_btn_send')}
            </button>
          </form>

          {/* Simulated 2-Way Phone Thread */}
          {conversation && (
            <div className="sms-thread-container">
              <div className="sms-thread-header">
                <span>📱 {t('sms_reply_label')}</span>
                <span className="sms-thread-time">{conversation.timestamp}</span>
              </div>

              {/* Citizen Outgoing Bubble */}
              <div className="sms-bubble-wrapper sms-out">
                <div className="sms-bubble sms-bubble-out">
                  <span className="sms-bubble-sender">You ({conversation.sender})</span>
                  <p>{conversation.sentText}</p>
                </div>
              </div>

              {/* Triage Pipeline Flag */}
              <div className="sms-triage-flag">
                <span>
                  🤖 AI: {conversation.ai?.match_decision === 'MATCH' ? `Matched Incident #${conversation.ai?.matched_incident_id}` : 'New Incident Created'}
                  {conversation.ai?.confidence_score && ` • ${Math.round(conversation.ai.confidence_score * 100)}% confidence`}
                </span>
                {conversation.autoEscalated && (
                  <span className="escalated-pill">⚡ {t('sms_auto_escalated')}</span>
                )}
              </div>

              {/* Anya System Incoming Bubble */}
              <div className="sms-bubble-wrapper sms-in">
                <div className="sms-bubble sms-bubble-in">
                  <span className="sms-bubble-sender">Anya Emergency Broadcast</span>
                  <p>{conversation.replyText}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

