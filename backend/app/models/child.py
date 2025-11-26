"""Child model with pseudonymous identification.

Requirements: 2.3 - Child enrollment in classes.
Requirements: 9.3 - Pseudonymous child identifiers for privacy.
"""
import uuid
from app import db


class Child(db.Model):
    """Represents a child enrolled in a class.
    
    Children are identified by a pseudonymous child_code for privacy.
    The child_code is used in events instead of PII.
    """
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    child_code = db.Column(db.String(100), unique=True, nullable=False)
    age = db.Column(db.Integer)
    
    # Relationships
    class_ = db.relationship('Class', back_populates='children')
    daily_metrics = db.relationship('ChildDailyMetrics', back_populates='child', lazy='dynamic')
    parent_links = db.relationship('ParentLink', back_populates='child', lazy='dynamic')
    
    def __init__(self, **kwargs):
        """Initialize child with auto-generated child_code if not provided."""
        if 'child_code' not in kwargs or not kwargs['child_code']:
            kwargs['child_code'] = self.generate_child_code()
        super().__init__(**kwargs)
    
    @staticmethod
    def generate_child_code():
        """Generate a unique pseudonymous identifier for a child.
        
        Returns:
            A unique string identifier (UUID-based).
        """
        return f"child_{uuid.uuid4().hex[:16]}"
    
    def __repr__(self):
        return f'<Child {self.child_code}>'
    
    def to_dict(self, include_class=False):
        """Serialize child to dictionary for JSON response.
        
        Note: child_code is included as it's the pseudonymous identifier.
        """
        data = {
            'id': self.id,
            'class_id': self.class_id,
            'display_name': self.display_name,
            'child_code': self.child_code,
            'age': self.age,
        }
        if include_class and self.class_:
            data['class'] = self.class_.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create a Child instance from a dictionary."""
        return cls(
            id=data.get('id'),
            class_id=data.get('class_id'),
            display_name=data.get('display_name'),
            child_code=data.get('child_code'),  # Will auto-generate if None
            age=data.get('age'),
        )
