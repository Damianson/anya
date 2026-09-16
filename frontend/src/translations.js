/**
 * Static translation dictionaries for Anya.
 * English (en) and Nigerian Pidgin (pcm).
 * Hardcoded static UI strings only — zero external API calls.
 */

export const TRANSLATIONS = {
  en: {
    app_title: "Anya",
    app_tagline: "Crisis Coordination Platform",
    role_label: "Active Role:",
    role_resident: "Resident",
    role_responder: "First Responder",
    
    // Language Toggle
    lang_toggle: "Language:",

    // Report Form
    form_title: "Submit Crisis Report",
    form_subtitle: "Reporting as:",
    field_desc: "Report Description",
    field_desc_placeholder: "Describe the situation, hazards, or immediate needs...",
    field_location: "Location / Landmark (optional)",
    field_location_placeholder: "e.g. Lekki-Epe Expressway by Ajah bridge",
    field_image: "Image URL (optional)",
    field_image_placeholder: "https://example.com/photo.jpg",
    btn_submit: "Submit Report",
    btn_submitting: "Analyzing & Submitting...",
    alert_success: "Report submitted successfully!",
    ai_decision_label: "AI Decision:",
    badge_matched: "Matched Incident #",
    badge_new: "New Incident Created",
    conflict_detected: "Conflict Detected:",
    ai_rationale_label: "AI Triage Rationale",
    ai_confidence: "confidence",

    // Low-Bandwidth SMS Simulator
    btn_sms_simulator: "📱 2G SMS Ingest Simulator",
    sms_modal_title: "Low-Bandwidth SMS Ingestion Gateway (2G / Feature Phone)",
    sms_modal_sub: "Simulates incoming citizen SMS from areas where cellular internet is down. Messages are automatically anonymized and triaged.",
    sms_sender_label: "Citizen Phone Number:",
    sms_message_label: "Inbound SMS Message:",
    sms_quick_scenarios: "Quick Crisis Scenarios (Nigeria):",
    sms_btn_send: "Send Inbound SMS",
    sms_btn_sending: "Transmitting 2G SMS...",
    sms_reply_label: "Simulated Citizen Handset (SMS Reply Received):",
    sms_auto_escalated: "Auto-Escalated to Critical (High Volume)",
    sms_badge_2g: "2G SMS Ingestion",

    // Incident List
    list_heading: "Active Incidents",
    btn_view_list: "List View",
    btn_view_map: "Map View",
    empty_incidents: "No incidents recorded yet. Submit a report to begin.",
    btn_view_details: "View Details",
    btn_viewing: "Viewing",
    meta_type: "Type:",
    meta_location: "Location:",
    meta_affected: "Affected:",
    meta_created: "Created:",

    // Detail View
    detail_heading: "Incident Details",
    detail_close: "✕ Close",
    detail_first_reported: "First Reported:",
    detail_last_updated: "Last Updated:",
    detail_linked_reports: "Linked Reports",
    detail_no_reports: "No linked reports available.",
    detail_active_response: "Active Response & Field Operations",
    detail_no_tasks: "No operational tasks dispatched yet.",
    badge_response_underway: "Response Underway",
    badge_teams_active: "active",
    task_status_claimed: "In Progress",
    task_status_open: "Awaiting Responder",
    task_status_completed: "Completed",

    // Responder View
    responder_heading: "Emergency Responder Triage Board",
    responder_sub: "Review field reports, verify or dispute crisis events, and dispatch operational tasks.",
    btn_refresh: "↻ Refresh Triage",
    metric_attention: "Needing Attention (Disputed / Unverified)",
    metric_verified: "Verified Incidents",
    metric_total: "Total Tracked",
    verification_action: "Verification Action:",
    btn_verify: "Mark Verified",
    btn_verified: "✓ Verified",
    btn_dispute: "Mark Disputed",
    btn_disputed: "⚠ Disputed",
    btn_suggest_task: "+ Generate Suggested Task",
    btn_generating: "Generating...",
    btn_inspect: "Inspect Reports",
    tasks_heading: "Operational Tasks",
    no_tasks: "No tasks generated yet. Click 'Generate Suggested Task' to dispatch response.",
    btn_claim_task: "Claim Task",
    btn_claiming: "Claiming...",
    claimed_by_label: "Claimed by:",

    // Status & Urgency
    urgency_critical: "Critical",
    urgency_high: "High",
    urgency_medium: "Medium",
    urgency_low: "Low",
    state_unverified: "Unverified",
    state_corroborated: "Corroborated",
    state_verified: "Verified",
    state_disputed: "Disputed",
    state_resolved: "Resolved"
  },

  pcm: {
    app_title: "Anya",
    app_tagline: "Crisis Coordination System for Community",
    role_label: "Who You Be:",
    role_resident: "Resident / Citizen",
    role_responder: "Emergency Team",

    // Language Toggle
    lang_toggle: "Language:",

    // Report Form
    form_title: "Report Emergency / Wahala",
    form_subtitle: "You dey report as:",
    field_desc: "Wetyn Happen (Description)",
    field_desc_placeholder: "Talk wetyn dey happen, danger wey dey, or wetyn people need quick-quick...",
    field_location: "Which Area / Landmark (if you know am)",
    field_location_placeholder: "e.g. Lekki-Epe expressway near Ajah bridge",
    field_image: "Photo Link (URL, if e dey)",
    field_image_placeholder: "https://example.com/photo.jpg",
    btn_submit: "Send Report Now",
    btn_submitting: "AI Dey Check & Send...",
    alert_success: "Report don enter successfully!",
    ai_decision_label: "AI Decision:",
    badge_matched: "E Match Incident #",
    badge_new: "New Incident Don Open",
    conflict_detected: "Gbege / Contradiction Dey:",
    ai_rationale_label: "Why AI Reason Am",
    ai_confidence: "sureness",

    // Low-Bandwidth SMS Simulator
    btn_sms_simulator: "📱 SMS Wey No Need Internet",
    sms_modal_title: "Channel Wey Dey Receive SMS (2G / Small Phone)",
    sms_modal_sub: "Dey collect SMS from area where internet don cut. System dey hide phone number make citizen safe.",
    sms_sender_label: "Phone Number Wey Send Am:",
    sms_message_label: "SMS Wey Enter:",
    sms_quick_scenarios: "Quick Story (Naija Crisis):",
    sms_btn_send: "Send Inbound SMS",
    sms_btn_sending: "SMS Dey Enter Network...",
    sms_reply_label: "Phone Wey Receive Reply:",
    sms_auto_escalated: "Urgency Don High to Critical!",
    sms_badge_2g: "2G SMS Channel",

    // Incident List
    list_heading: "Wahala / Incidents Wey Dey Ground",
    btn_view_list: "List View",
    btn_view_map: "Map View",
    empty_incidents: "No wahala report for now. Send report if something happen.",
    btn_view_details: "See Full Story",
    btn_viewing: "Dey Look Am",
    meta_type: "Kind of Wahala:",
    meta_location: "Area:",
    meta_affected: "People Wey Affect:",
    meta_created: "Time Wey E Enter:",

    // Detail View
    detail_heading: "Incident Details",
    detail_close: "✕ Close Am",
    detail_first_reported: "First Time Wey We Hear Am:",
    detail_last_updated: "Last Time We Update Am:",
    detail_linked_reports: "Reports Wey Connect to This Incident",
    detail_no_reports: "No report connect yet.",
    detail_active_response: "Work Wey Responders Dey Do for Ground",
    detail_no_tasks: "Nobody never pick work for this incident yet.",
    badge_response_underway: "Help Dey Ground",
    badge_teams_active: "team dey work",
    task_status_claimed: "Work Dey Go On",
    task_status_open: "Dey Wait Make Person Pick Am",
    task_status_completed: "Work Don Finish",

    // Responder View
    responder_heading: "Emergency Team Triage Workspace",
    responder_sub: "Check field reports, confirm true story or dispute false alarm, and assign work.",
    btn_refresh: "↻ Refresh Triage",
    metric_attention: "Things Wey Need Attention Quick",
    metric_verified: "Incidents Wey Don Confirm",
    metric_total: "Total Incidents Wey Dey Ground",
    verification_action: "Wetyn You Wan Do:",
    btn_verify: "Confirm Am (Verified)",
    btn_verified: "✓ Confirmed",
    btn_dispute: "Dispute Am (False Alarm)",
    btn_disputed: "⚠ Disputed",
    btn_suggest_task: "+ Suggest Wetyn To Do",
    btn_generating: "AI Dey Think Work...",
    btn_inspect: "Check All Reports",
    tasks_heading: "Work Wey Dey Ground",
    no_tasks: "No task yet. Click 'Suggest Wetyn To Do' make AI assign work.",
    btn_claim_task: "Take This Work",
    btn_claiming: "Dey Claim Am...",
    claimed_by_label: "Person Wey Take Am:",

    // Status & Urgency
    urgency_critical: "Danger / Critical",
    urgency_high: "Very Serious",
    urgency_medium: "Normal Wahala",
    urgency_low: "Small Wahala",
    state_unverified: "Never Confirm",
    state_corroborated: "People Corroborate Am",
    state_verified: "Confirmed True",
    state_disputed: "Disputed / Contradict",
    state_resolved: "Don Settle"
  }
};

