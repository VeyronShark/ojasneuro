"""Analytics routes for metrics and skill profiles.

Requirements: 4.1 - GET /classes/{id}/metrics returns class metrics with date range
Requirements: 4.2 - GET /children/{id}/metrics returns child metrics
Requirements: 4.3 - GET /children/{id}/skill-profile returns child skill scores
Requirements: 4.4 - GET /classes/{id}/skill-overview returns class skill distribution
"""
from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.class_service import ClassService, ClassNotFoundError, AccessDeniedError
from app.services.analytics_service import (
    AnalyticsService,
    DateRange,
    ChildNotFoundError,
    ClassNotFoundError as AnalyticsClassNotFoundError,
)
from app.models.child import Child
from app import db

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/school/<int:school_id>', methods=['GET'])
@jwt_required()
def get_school_metrics(school_id: int):
    """Get aggregated metrics for a school.
    
    Returns:
        200: School metrics data
        401: If not authenticated
        403: If user doesn't have access to the school
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user belongs to this school
        if user.school_id != school_id:
            return jsonify({
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'You do not have access to this school'
                }
            }), 403
        
        # Get school metrics from the database
        from app.models import School, SchoolWeeklyMetrics
        school = db.session.get(School, school_id)
        if not school:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'School with id {school_id} not found'
                }
            }), 404
        
        # Get latest weekly metrics
        latest_metrics = SchoolWeeklyMetrics.query.filter_by(
            school_id=school_id
        ).order_by(SchoolWeeklyMetrics.week_start_date.desc()).first()
        
        metrics_data = latest_metrics.metrics if latest_metrics else {}
        
        return jsonify({
            'school_id': school_id,
            'school_name': school.name,
            'enrolled_families': school.enrolled_families,
            'app_installs': school.app_installs,
            'metrics': metrics_data,
            'week_start_date': latest_metrics.week_start_date.isoformat() if latest_metrics else None
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401


def _parse_date_range(request) -> DateRange:
    """Parse date range from request query parameters.
    
    Defaults to last 30 days if not specified.
    """
    end_date_str = request.args.get('end_date')
    start_date_str = request.args.get('start_date')
    
    if end_date_str:
        try:
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()
    
    if start_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=30)
    
    return DateRange(start_date=start_date, end_date=end_date)


@analytics_bp.route('/classes/<int:class_id>/metrics', methods=['GET'])
@jwt_required()
def get_class_metrics(class_id: int):
    """Get aggregated metrics for a class.
    
    Query Parameters:
        start_date: Start date for filtering (ISO format, defaults to 30 days ago)
        end_date: End date for filtering (ISO format, defaults to today)
    
    Returns:
        200: Class metrics data
        401: If not authenticated
        403: If user doesn't have access to the class
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the class
        ClassService.get_class(class_id, user)
        
        # Parse date range
        date_range = _parse_date_range(request)
        
        # Get metrics
        metrics = AnalyticsService.get_class_metrics(class_id, date_range)
        
        return jsonify(metrics.to_dict()), 200
        
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
    except (ClassNotFoundError, AnalyticsClassNotFoundError) as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@analytics_bp.route('/classes/<int:class_id>/skill-overview', methods=['GET'])
@jwt_required()
def get_class_skill_overview(class_id: int):
    """Get skill distribution overview for a class.
    
    Returns:
        200: Class skill overview data
        401: If not authenticated
        403: If user doesn't have access to the class
        404: If class not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the class
        ClassService.get_class(class_id, user)
        
        # Get skill overview
        overview = AnalyticsService.get_class_skill_overview(class_id)
        
        return jsonify(overview.to_dict()), 200
        
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
    except (ClassNotFoundError, AnalyticsClassNotFoundError) as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


def _get_child_with_access_check(child_id: int, user):
    """Get a child and verify user has access.
    
    Args:
        child_id: ID of the child
        user: Authenticated user
        
    Returns:
        Child instance
        
    Raises:
        ChildNotFoundError: If child doesn't exist
        AccessDeniedError: If user doesn't have access
    """
    child = db.session.get(Child, child_id)
    if child is None:
        raise ChildNotFoundError(f"Child with id {child_id} not found")
    
    # Verify user has access to the child's class
    ClassService.get_class(child.class_id, user)
    
    return child


@analytics_bp.route('/children/<int:child_id>/metrics', methods=['GET'])
@jwt_required()
def get_child_metrics(child_id: int):
    """Get aggregated metrics for a child.
    
    Query Parameters:
        start_date: Start date for filtering (ISO format, defaults to 30 days ago)
        end_date: End date for filtering (ISO format, defaults to today)
    
    Returns:
        200: Child metrics data
        401: If not authenticated
        403: If user doesn't have access to the child's class
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the child
        _get_child_with_access_check(child_id, user)
        
        # Parse date range
        date_range = _parse_date_range(request)
        
        # Get metrics
        metrics = AnalyticsService.get_child_metrics(child_id, date_range)
        
        return jsonify(metrics.to_dict()), 200
        
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
    except (ChildNotFoundError, ClassNotFoundError) as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@analytics_bp.route('/children/<int:child_id>/skill-profile', methods=['GET'])
@jwt_required()
def get_child_skill_profile(child_id: int):
    """Get skill profile for a child.
    
    Returns:
        200: Child skill profile data
        401: If not authenticated
        403: If user doesn't have access to the child's class
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the child
        _get_child_with_access_check(child_id, user)
        
        # Get skill profile
        profile = AnalyticsService.get_skill_profile(child_id)
        
        return jsonify(profile.to_dict()), 200
        
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
    except (ChildNotFoundError, ClassNotFoundError) as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
