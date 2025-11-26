"""Event model for storing raw app interaction data.

Requirements: 3.2 - Persist events to raw events store.
Requirements: 9.3 - Use only pseudonymous child identifiers.
"""
from app import db


class EventRaw(db.Model):
    """Represents a raw event from the mobile app.
    
    Events capture child interactions with puzzles/activities.
    Only pseudonymous child_code is stored, never PII.
    """
    __tablename__ = 'events_raw'
    
    id = db.Column(db.Integer, primary_key=True)
    child_code = db.Column(db.String(100), nullable=False, index=True)
    puzzle_id = db.Column(db.String(100), nullable=False)
    skill_tags = db.Column(db.JSON, nullable=False)  # List of skill tags
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'<EventRaw {self.id} child={self.child_code}>'
    
    @property
    def duration_seconds(self):
        """Calculate event duration in seconds."""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0
    
    def to_dict(self):
        """Serialize event to dictionary for JSON response.
        
        Note: Only child_code is included, never child display_name or PII.
        """
        return {
            'id': self.id,
            'child_code': self.child_code,
            'puzzle_id': self.puzzle_id,
            'skill_tags': self.skill_tags,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'completed': self.completed,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an EventRaw instance from a dictionary."""
        from datetime import datetime
        
        started_at = data.get('started_at')
        ended_at = data.get('ended_at')
        
        # Parse ISO format strings if needed
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        if isinstance(ended_at, str):
            ended_at = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
        
        return cls(
            id=data.get('id'),
            child_code=data.get('child_code'),
            puzzle_id=data.get('puzzle_id'),
            skill_tags=data.get('skill_tags'),
            started_at=started_at,
            ended_at=ended_at,
            completed=data.get('completed'),
        )
