"""Consent management routes.

Requirements: 7.1 - POST /consent stores consent record with timestamp and scope
Requirements: 7.2 - GET /children/{id}/consent-status returns current consent state
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.consent_service import ConsentService, ConsentError
from app.schemas.consent import ConsentSubmitSchema, ConsentStatusSchema

consent_bp = Blueprint('consent', __name__)


@consent_bp.route('/consent', methods=['POST'])
@jwt_required()
def submit_consent():
    """Submit parent consent for a child.
    
    Request Body:
        {
            "child_id": 1,
            "parent_id": 1,
            "consent_status": "granted",  # or "denied"
            "scope": "full"  # optional: "full", "limited", "analytics_only"
        }
        
    Returns:
        201: {
            "id": 1,
            "child_id": 1,
            "parent_id": 1,
            "consent_status": "granted",
            "consent_timestamp": "2024-01-15T10:00:00",
            "consent_scope": "full"
        }
        400: {"error": {"code": "VALIDATION_ERROR", "message": "..."}}
        401: If not authenticated
        404: If child not found
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    # Validate request data
    schema = ConsentSubmitSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid request data',
                'details': errors
            }
        }), 400
    
    try:
        parent_link = ConsentService.submit_consent(
            child_id=data['child_id'],
            parent_id=data['parent_id'],
            consent_status=data['consent_status'],
            scope=data.get('scope', 'full')
        )
        return jsonify(parent_link.to_dict()), 201
    except ConsentError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@consent_bp.route('/children/<int:child_id>/consent-status', methods=['GET'])
@jwt_required()
def get_consent_status(child_id: int):
    """Get consent status for a child.
    
    Args:
        child_id: ID of the child
        
    Returns:
        200: {
            "child_id": 1,
            "consent_status": "granted",
            "consent_timestamp": "2024-01-15T10:00:00",
            "consent_scope": "full",
            "is_consent_granted": true
        }
        401: If not authenticated
        404: If child not found
    """
    try:
        status = ConsentService.get_consent_status(child_id)
        return jsonify(status.to_dict()), 200
    except ConsentError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404


@consent_bp.route('/children/<int:child_id>/data', methods=['DELETE'])
@jwt_required()
def delete_child_data(child_id: int):
    """Delete a child's event data (GDPR compliance).
    
    Args:
        child_id: ID of the child
        
    Returns:
        200: {"message": "Child data deleted successfully"}
        401: If not authenticated
        404: If child not found
    """
    try:
        ConsentService.delete_child_data(child_id)
        return jsonify({'message': 'Child data deleted successfully'}), 200
    except ConsentError as e:
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
