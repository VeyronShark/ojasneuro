"""Event ingestion routes.

Requirements: 3.1 - POST /events validates events contain required fields
Requirements: 3.2 - POST /events persists valid events to raw events store
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.services.event_service import EventService

events_bp = Blueprint('events', __name__, url_prefix='/events')


@events_bp.route('', methods=['POST'])
@jwt_required()
def ingest_events():
    """Ingest a batch of events from the mobile app.
    
    Request Body:
        {
            "events": [
                {
                    "child_code": "child_abc123",
                    "puzzle_id": "puzzle_001",
                    "skill_tags": ["attention", "patience"],
                    "started_at": "2024-01-15T10:00:00Z",
                    "ended_at": "2024-01-15T10:05:00Z",
                    "completed": true
                },
                ...
            ]
        }
        
    Returns:
        200: {
            "total_received": 10,
            "total_accepted": 8,
            "total_rejected": 2,
            "errors": [
                {"index": 3, "errors": ["'puzzle_id' is required"]},
                ...
            ]
        }
        400: {"error": {"code": "VALIDATION_ERROR", "message": "..."}}
        401: If not authenticated
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Request body is required'
            }
        }), 400
    
    events_data = data.get('events')
    
    if not events_data:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': "'events' field is required"
            }
        }), 400
    
    if not isinstance(events_data, list):
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': "'events' must be a list"
            }
        }), 400
    
    if len(events_data) == 0:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': "'events' must contain at least one event"
            }
        }), 400
    
    if len(events_data) > 1000:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': "'events' cannot contain more than 1000 events"
            }
        }), 400
    
    # Process the events
    result = EventService.ingest_events(events_data)
    
    return jsonify(result.to_dict()), 200
