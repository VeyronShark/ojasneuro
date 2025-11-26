"""School management routes.

Requirements: 2.1 - GET /schools/{id}/summary returns school details
Requirements: 2.2 - GET /schools/{id}/classes returns classes belonging to school
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.school_service import (
    SchoolService,
    SchoolNotFoundError,
    AccessDeniedError,
)

schools_bp = Blueprint('schools', __name__, url_prefix='/schools')


@schools_bp.route('/<int:school_id>/summary', methods=['GET'])
@jwt_required()
def get_school_summary(school_id: int):
    """Get school summary including enrolled families and app installs.
    
    Returns:
        200: School summary data
        401: If not authenticated
        403: If user doesn't have access to the school
        404: If school not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        summary = SchoolService.get_school_summary(school_id, user)
        
        return jsonify(summary), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except AccessDeniedError as e:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': str(e)
            }
        }), 403
    except SchoolNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@schools_bp.route('/<int:school_id>/classes', methods=['GET'])
@jwt_required()
def get_school_classes(school_id: int):
    """Get all classes belonging to a school.
    
    Returns:
        200: List of classes
        401: If not authenticated
        403: If user doesn't have access to the school
        404: If school not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        classes = SchoolService.get_classes(school_id, user)
        
        return jsonify({
            'classes': [c.to_dict(include_teacher=True) for c in classes]
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except AccessDeniedError as e:
        return jsonify({
            'error': {
                'code': 'FORBIDDEN',
                'message': str(e)
            }
        }), 403
    except SchoolNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
