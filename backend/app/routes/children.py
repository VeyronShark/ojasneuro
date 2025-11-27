"""Child/Student management routes.

Requirements: 3.3, 4.4 - Student CRUD operations
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.child_service import (
    ChildService,
    ChildNotFoundError,
    ValidationError,
)
from app.services.class_service import AccessDeniedError

children_bp = Blueprint('children', __name__, url_prefix='/children')


@children_bp.route('', methods=['POST'])
@jwt_required()
def create_child():
    """Create a new child/student.
    
    Request body:
        display_name: Child's display name (required)
        class_id: ID of the class to enroll in (required)
        age: Child's age (optional)
    
    Returns:
        201: Created child
        400: If validation fails
        401: If not authenticated
        403: If user doesn't have permission
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        data = request.get_json() or {}
        
        new_child = ChildService.create_child(data, user)
        
        return jsonify({
            'child': new_child.to_dict()
        }), 201
        
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
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400


@children_bp.route('/<int:child_id>', methods=['GET'])
@jwt_required()
def get_child(child_id: int):
    """Get a child by ID.
    
    Returns:
        200: Child details
        401: If not authenticated
        403: If user doesn't have access to the child
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        child = ChildService.get_child(child_id, user)
        
        return jsonify({
            'child': child.to_dict(include_class=True)
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
    except ChildNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@children_bp.route('/<int:child_id>', methods=['PUT'])
@jwt_required()
def update_child(child_id: int):
    """Update a child.
    
    Request body:
        display_name: Child's display name (optional)
        age: Child's age (optional)
        class_id: ID of the class (optional, for moving to another class)
    
    Returns:
        200: Updated child
        400: If validation fails
        401: If not authenticated
        403: If user doesn't have permission
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        data = request.get_json() or {}
        
        updated_child = ChildService.update_child(child_id, data, user)
        
        return jsonify({
            'child': updated_child.to_dict(include_class=True)
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
    except ChildNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400


@children_bp.route('/<int:child_id>', methods=['DELETE'])
@jwt_required()
def delete_child(child_id: int):
    """Delete a child.
    
    Returns:
        200: Success message
        401: If not authenticated
        403: If user doesn't have permission
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        ChildService.delete_child(child_id, user)
        
        return jsonify({
            'message': 'Child deleted successfully'
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
    except ChildNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
