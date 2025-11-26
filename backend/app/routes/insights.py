"""Insight routes for child insights and activity suggestions.

Requirements: 5.1 - GET /children/{id}/insights returns generated insight text
Requirements: 5.2 - Include suggested activities when skill score is below class mean
Requirements: 5.3 - GET /skills/{tag}/suggestions returns activity suggestions
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.class_service import ClassService, ClassNotFoundError, AccessDeniedError
from app.services.insight_service import (
    InsightService,
    ChildNotFoundError,
    InvalidSkillTagError,
)
from app.models.child import Child
from app import db

insights_bp = Blueprint('insights', __name__)


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


@insights_bp.route('/children/<int:child_id>/insights', methods=['GET'])
@jwt_required()
def get_child_insights(child_id: int):
    """Get insights for a child based on skill scores relative to class averages.
    
    Returns:
        200: List of insights for each skill tag
        401: If not authenticated
        403: If user doesn't have access to the child's class
        404: If child not found
    """
    user_id = get_jwt_identity()
    
    try:
        user = AuthService.get_current_user(user_id)
        
        # Verify user has access to the child
        _get_child_with_access_check(child_id, user)
        
        # Get insights
        insights = InsightService.get_child_insights(child_id)
        
        return jsonify({
            'child_id': child_id,
            'insights': [insight.to_dict() for insight in insights]
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


@insights_bp.route('/skills/<string:skill_tag>/suggestions', methods=['GET'])
@jwt_required()
def get_skill_suggestions(skill_tag: str):
    """Get activity suggestions for a specific skill tag.
    
    Returns:
        200: List of activity suggestions
        400: If skill tag is invalid
        401: If not authenticated
    """
    user_id = get_jwt_identity()
    
    try:
        # Verify user is authenticated
        AuthService.get_current_user(user_id)
        
        # Get suggestions
        suggestions = InsightService.get_activity_suggestions(skill_tag)
        
        return jsonify({
            'skill_tag': skill_tag,
            'suggestions': suggestions
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except InvalidSkillTagError as e:
        return jsonify({
            'error': {
                'code': 'INVALID_SKILL_TAG',
                'message': str(e)
            }
        }), 400
