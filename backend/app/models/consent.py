"""Consent model for parent authorization.

Requirements: 7.1 - Store consent records with timestamp and scope.
"""
from datetime import datetime
from app import db


class ParentLink(db.Model):
    """Represents a parent-child relationship with consent status.
    
    Tracks parent authorization for collecting and displaying
    their child's individual data.
    """
    __tablename__ = 'parent_links'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    parent_id = db.Column(db.Integer, nullable=False)
    consent_status = db.Column(db.String(50), default='pending')  # 'pending', 'granted', 'denied'
    consent_timestamp = db.Column(db.DateTime)
    consent_scope = db.Column(db.String(100))  # Scope of consent granted
    
    # Relationships
    child = db.relationship('Child', back_populates='parent_links')
    
    def __repr__(self):
        return f'<ParentLink child={self.child_id} parent={self.parent_id} status={self.consent_status}>'
    
    def grant_consent(self, scope='full'):
        """Grant consent with timestamp."""
        self.consent_status = 'granted'
        self.consent_timestamp = datetime.utcnow()
        self.consent_scope = scope
    
    def deny_consent(self):
        """Deny consent with timestamp."""
        self.consent_status = 'denied'
        self.consent_timestamp = datetime.utcnow()
    
    def is_consent_granted(self):
        """Check if consent has been granted."""
        return self.consent_status == 'granted'
    
    def to_dict(self):
        """Serialize consent to dictionary for JSON response."""
        return {
            'id': self.id,
            'child_id': self.child_id,
            'parent_id': self.parent_id,
            'consent_status': self.consent_status,
            'consent_timestamp': self.consent_timestamp.isoformat() if self.consent_timestamp else None,
            'consent_scope': self.consent_scope,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a ParentLink instance from a dictionary."""
        consent_timestamp = data.get('consent_timestamp')
        if isinstance(consent_timestamp, str):
            consent_timestamp = datetime.fromisoformat(consent_timestamp.replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            child_id=data.get('child_id'),
            parent_id=data.get('parent_id'),
            consent_status=data.get('consent_status', 'pending'),
            consent_timestamp=consent_timestamp,
            consent_scope=data.get('consent_scope'),
        )
