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
    """Get all children enrolled in a class with their metrics.
    
    Returns:
        200: List of children with engagement metrics
        401: If not authenticated
        403: If user doesn't have access to the class
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        from datetime import date, timedelta
        from app.models.event import EventRaw
        from app.models.metrics import ChildDailyMetrics
        from sqlalchemy import func
        
        user = AuthService.get_current_user(user_id)
        children = ClassService.get_children(class_id, user)
        
        # Prepare enriched children data with metrics
        enriched_children = []
        
        for child in children:
            child_data = child.to_dict()
            
            # Get last 30 days of data for metrics
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            # Get events for this child in the last 30 days
            events = EventRaw.query.filter(
                EventRaw.child_code == child.child_code,
                func.date(EventRaw.started_at) >= start_date,
                func.date(EventRaw.started_at) <= end_date
            ).all()
            
            # Calculate total sessions
            total_sessions = len(events)
            
            # Calculate avg sessions per day (over 30 days)
            avg_sessions_per_day = total_sessions / 30.0 if total_sessions > 0 else 0
            
            # Determine engagement level
            if avg_sessions_per_day >= 1.5:
                engagement = 'high'
            elif avg_sessions_per_day >= 0.5:
                engagement = 'medium'
            else:
                engagement = 'low'
            
            # Calculate trend (compare last 7 days vs previous 7 days)
            last_7_days_start = end_date - timedelta(days=7)
            prev_7_days_start = end_date - timedelta(days=14)
            
            last_7_sessions = len([e for e in events if e.started_at.date() >= last_7_days_start])
            prev_7_sessions = len([e for e in events if prev_7_days_start <= e.started_at.date() < last_7_days_start])
            
            if last_7_sessions > prev_7_sessions:
                trend = 'up'
            elif last_7_sessions < prev_7_sessions:
                trend = 'down'
            else:
                trend = 'stable'
            
            # Calculate weekly activity (last 7 days)
            weekly_activity = []
            for i in range(7):
                day_date = end_date - timedelta(days=6-i)
                day_sessions = len([e for e in events if e.started_at.date() == day_date])
                weekly_activity.append(day_sessions)
            
            # Add metrics to child data
            child_data['metrics'] = {
                'engagement': engagement,
                'avg_sessions_per_day': round(avg_sessions_per_day, 2),
                'trend': trend,
                'weekly_activity': weekly_activity,
                'total_sessions_30d': total_sessions
            }
            
            enriched_children.append(child_data)
        
        return jsonify({
            'children': enriched_children
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
