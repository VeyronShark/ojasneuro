"""Authentication routes for login, logout, signup, and user profile.

Requirements: 1.1 - POST /auth/login returns token and profile for valid credentials
Requirements: 1.2 - POST /auth/login returns 401 for invalid credentials
Requirements: 1.3 - POST /auth/logout invalidates session
Requirements: 1.4 - GET /me returns current user profile and role
Requirements: 1.5 - Protected endpoints require authentication
"""
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from app.services.auth_service import AuthService, AuthenticationError, ValidationError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def require_auth(f):
    """Decorator to require authentication for an endpoint.
    
    This wraps jwt_required and provides consistent error handling.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin role for an endpoint."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Admin access required'
                }
            }), 403
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
        
    Returns:
        200: {"token": "...", "user": {...}}
        401: {"error": {"code": "AUTHENTICATION_ERROR", "message": "..."}}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    email = data.get('email')
    password = data.get('password')
    
    try:
        teacher, token = AuthService.login(email, password)
        
        return jsonify({
            'token': token,
            'user': teacher.to_dict()
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Invalidate the current JWT token.
    
    Returns:
        200: {"message": "Successfully logged out"}
        401: If not authenticated
    """
    jwt_data = get_jwt()
    jti = jwt_data['jti']
    
    AuthService.logout(jti)
    
    return jsonify({
        'message': 'Successfully logged out'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get the current authenticated user's profile.
    
    Returns:
        200: {"user": {...}}
        401: If not authenticated
    """
    user_id = get_jwt_identity()
    
    try:
        teacher = AuthService.get_current_user(user_id)
        return jsonify({
            'user': teacher.to_dict(include_school=True)
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user account.
    
    Request Body:
        {
            "email": "user@example.com",
            "password": "password123",
            "name": "John Doe",
            "role": "teacher" or "admin",
            "school_id": 1,  // Required for teachers
            "school_name": "My School"  // Required for admins
        }
        
    Returns:
        201: {"token": "...", "user": {...}}
        400: {"error": {"code": "VALIDATION_ERROR", "message": "..."}}
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    try:
        teacher, token = AuthService.signup(
            email=data.get('email'),
            password=data.get('password'),
            name=data.get('name'),
            role=data.get('role', 'teacher'),
            school_id=data.get('school_id'),
            school_name=data.get('school_name')
        )
        
        return jsonify({
            'token': token,
            'user': teacher.to_dict(include_school=True)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401


@auth_bp.route('/schools', methods=['GET'])
def get_schools():
    """Get list of schools for signup dropdown.
    
    Returns:
        200: {"schools": [...]}
    """
    schools = AuthService.get_schools()
    return jsonify({
        'schools': [school.to_dict() for school in schools]
    }), 200
