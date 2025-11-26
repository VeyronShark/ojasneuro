"""Authentication service for user login, logout, and token management.

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


class AuthenticationError(Exception):
    """Raised when authentication fails."""
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
