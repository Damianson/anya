from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from models import db, Incident, Report, Task
from ai_service import analyze_report, generate_suggested_task

api_bp = Blueprint('api', __name__)

@api_bp.route('/reports', methods=['POST'])
def create_report():
    """
    Ingest a new report.
    Pipeline:
    1. Validate input payload.
    2. Retrieve recent active incidents (last 15).
    3. Execute single Gemini LLM call to extract details, check for duplicate matching,
       and detect contradictions.
    4. Link to existing incident (if matched) or create a new incident.
    5. Update verification state ('corroborated' or 'disputed') if matched.
    6. Save Report and return structured JSON.
    7. Fallback gracefully on any LLM failure (zero data loss).
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON request body'}), 400

    raw_text = data.get('raw_text')
    if not raw_text or not isinstance(raw_text, str) or not raw_text.strip():
        return jsonify({'error': 'Missing required field: raw_text'}), 400

    reporter_label = data.get('reporter_label', 'resident')
    image_url = data.get('image_url')

    # Query the last 15 active incidents for duplicate and conflict comparison
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(15).all()
    incidents_payload = [inc.to_dict() for inc in recent_incidents]

    # Single LLM API call (with built-in fallback)
    ai_result = analyze_report(
        raw_text=raw_text.strip(),
        reporter_label=reporter_label,
        active_incidents=incidents_payload
    )
    ai_data = ai_result['data']

    target_incident = None
    incident_id = None

    # Handle Matching vs New Incident
    if ai_data.get('match_decision') == 'MATCH' and ai_data.get('matched_incident_id'):
        matched_id = ai_data['matched_incident_id']
        matched_incident = db.session.get(Incident, matched_id)

        if matched_incident:
            target_incident = matched_incident
            incident_id = matched_incident.id

            # Conflict & Verification State Handling
            if ai_data.get('has_contradiction'):
                target_incident.verification_state = 'disputed'
            else:
                if target_incident.verification_state == 'unverified':
                    target_incident.verification_state = 'corroborated'

            # Update affected estimate if new report provides one and incident didn't have one
            if ai_data.get('people_affected_estimate') and not target_incident.people_affected_estimate:
                target_incident.people_affected_estimate = ai_data['people_affected_estimate']

            target_incident.updated_at = datetime.now(timezone.utc)

    # If not matched or matched ID was invalid, create a new Incident
    if not target_incident:
        clean_text = raw_text.strip()
        first_line = clean_text.split('\n')[0]
        fallback_title = first_line[:57] + '...' if len(first_line) > 60 else first_line
        title = ai_data.get('suggested_title') or fallback_title or 'Reported Incident'

        target_incident = Incident(
            title=title,
            type=ai_data.get('incident_type', 'general'),
            location_text=ai_data.get('location', 'Unknown'),
            urgency=ai_data.get('urgency', 'medium'),
            verification_state='unverified',
            people_affected_estimate=ai_data.get('people_affected_estimate')
        )
        db.session.add(target_incident)
        db.session.flush()  # Generate target_incident.id before report linking
        incident_id = target_incident.id

    # Create and persist the Report
    report = Report(
        incident_id=incident_id,
        raw_text=raw_text.strip(),
        image_url=image_url,
        reporter_label=reporter_label,
        ai_reasoning=ai_data.get('reasoning_snippet'),
        ai_confidence=ai_data.get('confidence_score')
    )
    db.session.add(report)
    db.session.commit()

    response_payload = {
        'report': report.to_dict(),
        'incident': target_incident.to_dict(),
        'ai': {
            'status': ai_result.get('status'),
            'fallback_reason': ai_result.get('fallback_reason'),
            'match_decision': ai_data.get('match_decision'),
            'matched_incident_id': ai_data.get('matched_incident_id'),
            'has_contradiction': ai_data.get('has_contradiction'),
            'contradiction_reason': ai_data.get('contradiction_reason'),
            'confidence_score': ai_data.get('confidence_score'),
            'reasoning_snippet': ai_data.get('reasoning_snippet'),
            'extracted': {
                'incident_type': ai_data.get('incident_type'),
                'location': ai_data.get('location'),
                'urgency': ai_data.get('urgency'),
                'people_affected_estimate': ai_data.get('people_affected_estimate'),
                'suggested_title': ai_data.get('suggested_title')
            }
        }
    }

    return jsonify(response_payload), 201


@api_bp.route('/incidents', methods=['GET'])
def list_incidents():
    """
    List all incidents, ordered from newest to oldest, including their tasks, report count,
    and latest AI triage rationale and confidence score.
    """
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    results = []
    for inc in incidents:
        data = inc.to_dict()
        data['tasks'] = [t.to_dict() for t in inc.tasks]
        data['report_count'] = len(inc.reports)
        
        # Surface the latest or most significant report's AI reasoning
        reports_with_ai = [r for r in inc.reports if r.ai_reasoning]
        if reports_with_ai:
            # Prefer corroboration/conflict reports (id > 1) if available, or the latest
            chosen_report = reports_with_ai[-1]
            data['latest_ai_reasoning'] = chosen_report.ai_reasoning
            data['latest_ai_confidence'] = chosen_report.ai_confidence
        else:
            data['latest_ai_reasoning'] = None
            data['latest_ai_confidence'] = None
            
        results.append(data)
    return jsonify(results), 200


@api_bp.route('/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    """
    Retrieve incident detail by ID, including its linked reports, tasks, and primary AI rationale.
    """
    incident = db.session.get(Incident, id)
    if not incident:
        return jsonify({'error': f'Incident {id} not found'}), 404

    incident_data = incident.to_dict()
    reports = [r.to_dict() for r in incident.reports]
    incident_data['reports'] = reports
    incident_data['tasks'] = [t.to_dict() for t in incident.tasks]
    
    reports_with_ai = [r for r in reports if r.get('ai_reasoning')]
    if reports_with_ai:
        chosen = reports_with_ai[-1]
        incident_data['latest_ai_reasoning'] = chosen.get('ai_reasoning')
        incident_data['latest_ai_confidence'] = chosen.get('ai_confidence')
    else:
        incident_data['latest_ai_reasoning'] = None
        incident_data['latest_ai_confidence'] = None

    return jsonify(incident_data), 200


@api_bp.route('/incidents/<int:id>/verify', methods=['POST'])
def verify_incident(id):
    """
    Human first responder action: Authoritatively mark an incident as verified.
    """
    incident = db.session.get(Incident, id)
    if not incident:
        return jsonify({'error': f'Incident {id} not found'}), 404

    incident.verification_state = 'verified'
    incident.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    incident_data = incident.to_dict()
    incident_data['reports'] = [r.to_dict() for r in incident.reports]
    incident_data['tasks'] = [t.to_dict() for t in incident.tasks]
    return jsonify(incident_data), 200


@api_bp.route('/incidents/<int:id>/dispute', methods=['POST'])
def dispute_incident(id):
    """
    Human first responder action: Authoritatively mark an incident as disputed.
    """
    incident = db.session.get(Incident, id)
    if not incident:
        return jsonify({'error': f'Incident {id} not found'}), 404

    incident.verification_state = 'disputed'
    incident.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    incident_data = incident.to_dict()
    incident_data['reports'] = [r.to_dict() for r in incident.reports]
    incident_data['tasks'] = [t.to_dict() for t in incident.tasks]
    return jsonify(incident_data), 200


@api_bp.route('/incidents/<int:id>/tasks/generate', methods=['POST'])
def generate_task_for_incident(id):
    """
    AI-assisted action: Suggests and creates an actionable task for a verified incident.
    """
    incident = db.session.get(Incident, id)
    if not incident:
        return jsonify({'error': f'Incident {id} not found'}), 404

    task_desc = generate_suggested_task(incident.to_dict())

    task = Task(
        incident_id=id,
        description=task_desc,
        status='open'
    )
    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@api_bp.route('/tasks/<int:id>/claim', methods=['POST'])
def claim_task(id):
    """
    Human responder action: Claim an open task to execute.
    """
    task = db.session.get(Task, id)
    if not task:
        return jsonify({'error': f'Task {id} not found'}), 404

    data = request.get_json(silent=True) or {}
    claimed_by = data.get('claimed_by', 'First Responder')

    task.status = 'claimed'
    task.claimed_by = claimed_by
    db.session.commit()

    return jsonify(task.to_dict()), 200

