"""Class management routes.

Requirements: 2.3 - GET /classes/{id}/children returns children enrolled in class
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.class_service import (
    ClassService,
    ClassNotFoundError,
    AccessDeniedError,
)

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('/<int:class_id>/children', methods=['GET'])
@jwt_required()
def get_class_children(class_id: int):
    """Get all children enrolled in a class.
    
    Returns:
        200: List of children
        401: If not authenticated
        403: If user doesn't have access to the class
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        children = ClassService.get_children(class_id, user)
        
        return jsonify({
            'children': [child.to_dict() for child in children]
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
    except ClassNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
