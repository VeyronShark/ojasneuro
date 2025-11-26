"""Class model for grouping children.

Requirements: 2.2 - Class management within schools.
Requirements: 2.3 - Children enrollment in classes.
"""
from app import db


class Class(db.Model):
    """Represents a class/group of children taught by teachers.
    
    Classes belong to a school and contain enrolled children.
    Each class has a primary teacher assigned.
    """
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    grade_level = db.Column(db.String(50))
    primary_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    
    # Relationships
    school = db.relationship('School', back_populates='classes')
    primary_teacher = db.relationship('Teacher', back_populates='primary_classes')
    children = db.relationship('Child', back_populates='class_', lazy='dynamic')
    weekly_metrics = db.relationship('ClassWeeklyMetrics', back_populates='class_', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.name}>'
    
    def to_dict(self, include_teacher=False, include_children=False):
        """Serialize class to dictionary for JSON response."""
        data = {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'grade_level': self.grade_level,
            'primary_teacher_id': self.primary_teacher_id,
        }
        if include_teacher and self.primary_teacher:
            data['primary_teacher'] = self.primary_teacher.to_dict()
        if include_children:
            data['children'] = [child.to_dict() for child in self.children]
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create a Class instance from a dictionary."""
        return cls(
            id=data.get('id'),
            school_id=data.get('school_id'),
            name=data.get('name'),
            grade_level=data.get('grade_level'),
            primary_teacher_id=data.get('primary_teacher_id'),
        )
