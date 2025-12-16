"""
Database models for customer session data.
"""

from datetime import datetime
from app import db


class CustomerSession(db.Model):
    """Model for storing customer session data."""
    
    __tablename__ = 'customer_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(255), nullable=False, index=True)
    region = db.Column(db.String(100), nullable=False, index=True)
    sessions = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(255), nullable=False, index=True)
    destination = db.Column(db.String(255), nullable=False, index=True)
    time_consumed = db.Column(db.Integer, nullable=True, index=True)  # Time in minutes
    observation = db.Column(db.Text, nullable=True)
    
    # Highlight fields for notable findings
    has_highlight = db.Column(db.Boolean, default=False, index=True)
    highlight_url = db.Column(db.String(500), nullable=True)  # Jira/Zendesk URL
    highlight_type = db.Column(db.String(100), nullable=True)  # Dropdown selection
    highlight_details = db.Column(db.Text, nullable=True)  # For "Other" option
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'customer': self.customer,
            'region': self.region,
            'sessions': self.sessions,
            'source': self.source,
            'destination': self.destination,
            'time_consumed': self.time_consumed,
            'observation': self.observation,
            'has_highlight': self.has_highlight,
            'highlight_url': self.highlight_url,
            'highlight_type': self.highlight_type,
            'highlight_details': self.highlight_details,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<CustomerSession {self.customer} - {self.region}>'

