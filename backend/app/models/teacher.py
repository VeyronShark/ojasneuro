"""Teacher model with authentication support.

Requirements: 1.1 - Secure authentication for teachers and admins.
Requirements: 2.1 - Teacher management within schools.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Teacher(db.Model):
    """Represents a teacher or admin user in the platform.
    
    Teachers can manage classes and view child metrics within their
    assigned school. Admins have broader access to school-wide data.
    """
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'teacher' or 'admin'
    
    # Relationships
    school = db.relationship('School', back_populates='teachers')
    primary_classes = db.relationship('Class', back_populates='primary_teacher', lazy='dynamic')
    
    def __repr__(self):
        return f'<Teacher {self.email}>'
    
    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == 'admin'
    
    def to_dict(self, include_school=False):
        """Serialize teacher to dictionary for JSON response.
        
        Note: password_hash is never included for security.
        """
        data = {
            'id': self.id,
            'school_id': self.school_id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
        }
        if include_school and self.school:
            data['school'] = self.school.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create a Teacher instance from a dictionary.
        
        Note: Use set_password() separately to set the password.
        """
        teacher = cls(
            id=data.get('id'),
            school_id=data.get('school_id'),
            email=data.get('email'),
            name=data.get('name'),
            role=data.get('role', 'teacher'),
        )
        if 'password' in data:
            teacher.set_password(data['password'])
        return teacher
