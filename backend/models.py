from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_utc_now():
    """Return current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)

class Incident(db.Model):
    """
    Represents a crisis event or emergency situation.
    Can be linked to multiple reports and actionable tasks.
    """
    __tablename__ = 'incidents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # e.g., 'flood', 'fire', 'medical', 'infrastructure'
    location_text = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    urgency = db.Column(db.String(50), nullable=False)  # e.g., 'low', 'medium', 'high', 'critical'
    
    # State values: 'unverified', 'corroborated', 'verified', 'disputed', 'resolved'
    verification_state = db.Column(db.String(50), nullable=False, default='unverified')
    
    people_affected_estimate = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_utc_now)
    updated_at = db.Column(db.DateTime, nullable=False, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    reports = db.relationship('Report', backref='incident', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='incident', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Serialize model fields to a Python dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'location_text': self.location_text,
            'lat': self.lat,
            'lng': self.lng,
            'urgency': self.urgency,
            'verification_state': self.verification_state,
            'people_affected_estimate': self.people_affected_estimate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Incident {self.id}: {self.title} [{self.urgency}]>"


class Report(db.Model):
    """
    Represents an incoming report submitted by a resident, responder, or observer.
    Nullable incident_id allows unclustered or triage-pending reports.
    """
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)
    raw_text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    reporter_label = db.Column(db.String(100), nullable=False)  # e.g., 'resident', 'responder', 'bystander'
    ai_reasoning = db.Column(db.Text, nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_utc_now)

    def to_dict(self):
        """Serialize model fields to a Python dictionary."""
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'raw_text': self.raw_text,
            'image_url': self.image_url,
            'reporter_label': self.reporter_label,
            'ai_reasoning': self.ai_reasoning,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Report {self.id} (Incident {self.incident_id})>"


class Task(db.Model):
    """
    Represents an actionable task tied to an incident (e.g., 'Deliver water purification tablets').
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Status values: 'open', 'claimed', 'in_progress', 'done'
    status = db.Column(db.String(50), nullable=False, default='open')
    claimed_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=get_utc_now)

    def to_dict(self):
        """Serialize model fields to a Python dictionary."""
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'description': self.description,
            'status': self.status,
            'claimed_by': self.claimed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Task {self.id} [{self.status}] for Incident {self.incident_id}>"

