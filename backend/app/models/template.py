"""Template models for activity suggestions and messages.

Requirements: 5.3 - Activity suggestions for skills.
Requirements: 8.1 - Communication templates for parents.
"""
from app import db


class ActivitySuggestion(db.Model):
    """Stores activity suggestions for skill development.
    
    Teachers can retrieve suggestions based on skill tags
    to provide targeted support for children.
    """
    __tablename__ = 'activity_suggestions'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_tag = db.Column(db.String(50), nullable=False, index=True)
    activity_text = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<ActivitySuggestion {self.skill_tag}: {self.activity_text[:30]}...>'
    
    def to_dict(self):
        """Serialize suggestion to dictionary for JSON response."""
        return {
            'id': self.id,
            'skill_tag': self.skill_tag,
            'activity_text': self.activity_text,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an ActivitySuggestion instance from a dictionary."""
        return cls(
            id=data.get('id'),
            skill_tag=data.get('skill_tag'),
            activity_text=data.get('activity_text'),
        )


class MessageTemplate(db.Model):
    """Stores message templates for parent communication.
    
    Templates support multiple languages and different types
    (parent messages, handouts, etc.).
    """
    __tablename__ = 'message_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_type = db.Column(db.String(50), nullable=False, index=True)
    language = db.Column(db.String(10), default='en')
    content = db.Column(db.Text, nullable=False)
    
    # Unique constraint on template_type + language
    __table_args__ = (
        db.UniqueConstraint('template_type', 'language', name='uq_message_template'),
    )
    
    def __repr__(self):
        return f'<MessageTemplate {self.template_type} ({self.language})>'
    
    def to_dict(self):
        """Serialize template to dictionary for JSON response."""
        return {
            'id': self.id,
            'template_type': self.template_type,
            'language': self.language,
            'content': self.content,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a MessageTemplate instance from a dictionary."""
        return cls(
            id=data.get('id'),
            template_type=data.get('template_type'),
            language=data.get('language', 'en'),
            content=data.get('content'),
        )
