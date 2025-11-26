"""School model for multi-tenant educational platform.

Requirements: 2.1 - School management with enrolled families and app install counts.
"""
from app import db


class School(db.Model):
    """Represents an educational institution subscribing to the platform.
    
    Each school is a tenant in the multi-tenant system, with isolated
    data for classes, teachers, and children.
    """
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(50))
    primary_color = db.Column(db.String(7))  # Hex color code
    enrolled_families = db.Column(db.Integer, default=0)
    app_installs = db.Column(db.Integer, default=0)
    
    # Relationships
    classes = db.relationship('Class', back_populates='school', lazy='dynamic')
    teachers = db.relationship('Teacher', back_populates='school', lazy='dynamic')
    weekly_metrics = db.relationship('SchoolWeeklyMetrics', back_populates='school', lazy='dynamic')
    
    def __repr__(self):
        return f'<School {self.name}>'
    
    def to_dict(self):
        """Serialize school to dictionary for JSON response."""
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo,
            'primary_color': self.primary_color,
            'enrolled_families': self.enrolled_families,
            'app_installs': self.app_installs,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a School instance from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            logo=data.get('logo'),
            primary_color=data.get('primary_color'),
            enrolled_families=data.get('enrolled_families', 0),
            app_installs=data.get('app_installs', 0),
        )
