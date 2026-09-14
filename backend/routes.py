from flask import Blueprint, request, jsonify
from models import db, Incident, Report, Task

api_bp = Blueprint('api', __name__)

@api_bp.route('/reports', methods=['POST'])
def create_report():
    """
    Ingest a new report.
    Under Day 2 deterministic logic (no AI):
    - Creates a new Incident for this report (unless link_incident=False is provided).
    - Saves the Report with incident_id linked to the new Incident.
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Invalid JSON request body'}), 400

    raw_text = data.get('raw_text')
    if not raw_text or not isinstance(raw_text, str) or not raw_text.strip():
        return jsonify({'error': 'Missing required field: raw_text'}), 400

    reporter_label = data.get('reporter_label', 'resident')
    image_url = data.get('image_url')
    
    # By default, create and link a 1:1 Incident (allow explicitly disabling if desired)
    link_incident = data.get('link_incident', True)

    incident_id = None
    created_incident = None

    if link_incident:
        clean_text = raw_text.strip()
        first_line = clean_text.split('\n')[0]
        title = data.get('title') or (first_line[:57] + '...' if len(first_line) > 60 else first_line)
        incident_type = data.get('type', 'general')
        location_text = data.get('location_text', 'Unknown')
        urgency = data.get('urgency', 'medium')
        lat = data.get('lat')
        lng = data.get('lng')
        people_affected = data.get('people_affected_estimate')

        created_incident = Incident(
            title=title,
            type=incident_type,
            location_text=location_text,
            lat=lat,
            lng=lng,
            urgency=urgency,
            verification_state='unverified',
            people_affected_estimate=people_affected
        )
        db.session.add(created_incident)
        # Flush sends SQL to the database to generate created_incident.id within the transaction
        db.session.flush()
        incident_id = created_incident.id

    report = Report(
        incident_id=incident_id,
        raw_text=raw_text.strip(),
        image_url=image_url,
        reporter_label=reporter_label
    )
    db.session.add(report)
    db.session.commit()

    response = {
        'report': report.to_dict()
    }
    if created_incident:
        response['incident'] = created_incident.to_dict()

    return jsonify(response), 201


@api_bp.route('/incidents', methods=['GET'])
def list_incidents():
    """
    List all incidents, ordered from newest to oldest.
    """
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return jsonify([incident.to_dict() for incident in incidents]), 200


@api_bp.route('/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    """
    Retrieve incident detail by ID, including its linked reports and tasks.
    """
    incident = db.session.get(Incident, id)
    if not incident:
        return jsonify({'error': f'Incident {id} not found'}), 404

    incident_data = incident.to_dict()
    incident_data['reports'] = [r.to_dict() for r in incident.reports]
    incident_data['tasks'] = [t.to_dict() for t in incident.tasks]
    return jsonify(incident_data), 200
