"""Class management routes.

Requirements: 2.3 - GET /classes/{id}/children returns children enrolled in class
Requirements: 2.2, 4.4, 6.3, 6.4 - Class CRUD operations
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.class_service import (
    ClassService,
    ClassNotFoundError,
    AccessDeniedError,
    ValidationError,
)

classes_bp = Blueprint('classes', __name__, url_prefix='/classes')


@classes_bp.route('', methods=['POST'])
@jwt_required()
def create_class():
    """Create a new class.
    
    Request body:
        name: Class name (required)
        grade_level: Grade level (optional)
        primary_teacher_id: ID of primary teacher (optional)
    
    Returns:
        201: Created class
        400: If validation fails
        401: If not authenticated
        403: If user doesn't have permission
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        data = request.get_json() or {}
        
        new_class = ClassService.create_class(data, user)
        
        return jsonify({
            'class': new_class.to_dict(include_teacher=True)
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


@classes_bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def get_class(class_id: int):
    """Get a class by ID.
    
    Returns:
        200: Class details
        401: If not authenticated
        403: If user doesn't have access to the class
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        class_obj = ClassService.get_class(class_id, user)
        
        return jsonify({
            'class': class_obj.to_dict(include_teacher=True)
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


@classes_bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id: int):
    """Update a class.
    
    Request body:
        name: Class name (optional)
        grade_level: Grade level (optional)
        primary_teacher_id: ID of primary teacher (optional)
    
    Returns:
        200: Updated class
        400: If validation fails
        401: If not authenticated
        403: If user doesn't have permission
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        data = request.get_json() or {}
        
        updated_class = ClassService.update_class(class_id, data, user)
        
        return jsonify({
            'class': updated_class.to_dict(include_teacher=True)
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
    except ValidationError as e:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400


@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id: int):
    """Delete a class.
    
    Returns:
        200: Success message
        401: If not authenticated
        403: If user doesn't have permission
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        ClassService.delete_class(class_id, user)
        
        return jsonify({
            'message': 'Class deleted successfully'
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
