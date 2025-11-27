"""Authentication service for user login, logout, signup, and token management.

Requirements: 1.1 - Valid credentials return authentication token and user profile
Requirements: 1.2 - Invalid credentials return 401
Requirements: 1.3 - Logout invalidates session
Requirements: 1.4 - /me endpoint returns current user profile and role
"""
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    get_jwt,
)
from werkzeug.security import check_password_hash

from app import db, blacklisted_tokens
from app.models.teacher import Teacher
from app.models.school import School


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def login(email: str, password: str) -> tuple[Teacher, str]:
        """Authenticate user and return user with JWT token.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (Teacher instance, JWT token string)
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        if not email or not password:
            raise AuthenticationError("Email and password are required")
        
        # Find user by email
        teacher = Teacher.query.filter_by(email=email).first()
        
        if teacher is None:
            raise AuthenticationError("Invalid credentials")
        
        # Verify password
        if not teacher.check_password(password):
            raise AuthenticationError("Invalid credentials")
        
        # Generate JWT token with user identity (must be string)
        token = create_access_token(
            identity=str(teacher.id),
            additional_claims={
                'email': teacher.email,
                'role': teacher.role,
                'school_id': teacher.school_id
            }
        )
        
        return teacher, token
    
    @staticmethod
    def logout(jti: str) -> bool:
        """Invalidate a JWT token by adding it to the blacklist.
        
        Args:
            jti: JWT token identifier (from get_jwt()['jti'])
            
        Returns:
            True if logout was successful
        """
        blacklisted_tokens.add(jti)
        return True
    
    @staticmethod
    def get_current_user(user_id: str) -> Teacher:
        """Get the current authenticated user.
        
        Args:
            user_id: User ID from JWT identity (as string)
            
        Returns:
            Teacher instance
            
        Raises:
            AuthenticationError: If user not found
        """
        teacher = db.session.get(Teacher, int(user_id))
        
        if teacher is None:
            raise AuthenticationError("User not found")
        
        return teacher
    
    @staticmethod
    def validate_token(jti: str) -> bool:
        """Check if a token is still valid (not blacklisted).
        
        Args:
            jti: JWT token identifier
            
        Returns:
            True if token is valid, False if blacklisted
        """
        return jti not in blacklisted_tokens

    @staticmethod
    def signup(email: str, password: str, name: str, role: str = 'teacher', 
               school_id: int = None, school_name: str = None) -> tuple[Teacher, str]:
        """Register a new user and return user with JWT token.
        
        Args:
            email: User's email address
            password: User's password
            name: User's display name
            role: User role ('teacher' or 'admin')
            school_id: Existing school ID to join (for teachers)
            school_name: New school name to create (for admins)
            
        Returns:
            Tuple of (Teacher instance, JWT token string)
            
        Raises:
            ValidationError: If validation fails
            AuthenticationError: If signup fails
        """
        # Validate required fields
        if not email or not password or not name:
            raise ValidationError("Email, password, and name are required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters")
        
        if role not in ('teacher', 'admin'):
            raise ValidationError("Role must be 'teacher' or 'admin'")
        
        # Check if email already exists
        existing = Teacher.query.filter_by(email=email).first()
        if existing:
            raise ValidationError("Email already registered")
        
        # Handle school assignment
        if role == 'admin':
            # Admins create a new school
            if not school_name:
                raise ValidationError("School name is required for admin signup")
            
            school = School(
                name=school_name,
                logo="🏫",
                primary_color="#4a90e2",
                enrolled_families=0,
                app_installs=0
            )
            db.session.add(school)
            db.session.flush()  # Get the school ID
            school_id = school.id
        else:
            # Teachers join an existing school
            if not school_id:
                raise ValidationError("School selection is required for teacher signup")
            
            school = db.session.get(School, school_id)
            if not school:
                raise ValidationError("Selected school not found")
        
        # Create the teacher/admin user
        teacher = Teacher(
            school_id=school_id,
            email=email,
            name=name,
            role=role
        )
        teacher.set_password(password)
        
        db.session.add(teacher)
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(
            identity=str(teacher.id),
            additional_claims={
                'email': teacher.email,
                'role': teacher.role,
                'school_id': teacher.school_id
            }
        )
        
        return teacher, token

    @staticmethod
    def get_schools() -> list[School]:
        """Get all schools for signup dropdown.
        
        Returns:
            List of School instances
        """
        return School.query.order_by(School.name).all()
