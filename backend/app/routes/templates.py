"""Template routes for parent communication templates and handouts.

Requirements: 8.1 - GET /templates/parent-message returns template text for specified language
Requirements: 8.2 - GET /templates/handout returns formatted content (text or PDF)
"""
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import AuthService, AuthenticationError
from app.services.template_service import (
    TemplateService,
    TemplateNotFoundError,
    InvalidTemplateTypeError,
    DEFAULT_LANGUAGE,
)

templates_bp = Blueprint('templates', __name__)


@templates_bp.route('/templates/parent-message', methods=['GET'])
@jwt_required()
def get_parent_message():
    """Get parent message template for the specified language.
    
    Query Parameters:
        language: Language code (default: 'en')
    
    Returns:
        200: Template content
        401: If not authenticated
        404: If template not found
    """
    user_id = get_jwt_identity()
    
    try:
        # Verify user is authenticated
        AuthService.get_current_user(user_id)
        
        # Get language from query params
        language = request.args.get('language', DEFAULT_LANGUAGE)
        
        # Get template
        content = TemplateService.get_parent_message(language)
        
        return jsonify({
            'template_type': 'parent_message',
            'language': language,
            'content': content
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except TemplateNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@templates_bp.route('/templates/handout', methods=['GET'])
@jwt_required()
def get_handout():
    """Get handout template in the specified format.
    
    Query Parameters:
        language: Language code (default: 'en')
        format: Output format ('text' or 'pdf', default: 'text')
    
    Returns:
        200: Template content (text or PDF)
        401: If not authenticated
        404: If template not found
    """
    user_id = get_jwt_identity()
    
    try:
        # Verify user is authenticated
        AuthService.get_current_user(user_id)
        
        # Get parameters from query
        language = request.args.get('language', DEFAULT_LANGUAGE)
        format_type = request.args.get('format', 'text')
        
        # Get template
        content = TemplateService.get_handout(format=format_type, language=language)
        
        if format_type == 'pdf':
            return Response(
                content,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': 'attachment; filename=handout.pdf'
                }
            )
        
        return jsonify({
            'template_type': 'handout',
            'language': language,
            'content': content
        }), 200
        
    except AuthenticationError as e:
        return jsonify({
            'error': {
                'code': 'AUTHENTICATION_ERROR',
                'message': str(e)
            }
        }), 401
    except TemplateNotFoundError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
