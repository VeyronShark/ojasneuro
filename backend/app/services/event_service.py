"""Event ingestion service for processing mobile app events.

Requirements: 3.1 - Validate events contain child_id, puzzle_id, skill_tags, timestamps, completion_status
Requirements: 3.2 - Persist valid events to raw events store
Requirements: 3.3 - Reject invalid events with validation errors
Requirements: 3.4 - Associate events with correct child record using pseudonymous token
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from marshmallow import ValidationError

from app import db
from app.models.event import EventRaw
from app.models.child import Child
from app.schemas.event import EventInputSchema, VALID_SKILL_TAGS


class EventValidationError(Exception):
    """Raised when event validation fails."""
    
    def __init__(self, message: str, errors: list[dict] = None):
        super().__init__(message)
        self.errors = errors or []


@dataclass
class IngestResult:
    """Result of batch event ingestion."""
    total_received: int = 0
    total_accepted: int = 0
    total_rejected: int = 0
    errors: list[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'total_received': self.total_received,
            'total_accepted': self.total_accepted,
            'total_rejected': self.total_rejected,
            'errors': self.errors
        }


class EventService:
    """Service for handling event ingestion operations."""
    
    @staticmethod
    def validate_event(event_data: dict) -> list[str]:
        """Validate a single event's data.
        
        Args:
            event_data: Dictionary containing event fields
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ['child_code', 'puzzle_id', 'skill_tags', 'started_at', 'ended_at', 'completed']
        for field_name in required_fields:
            if field_name not in event_data or event_data[field_name] is None:
                errors.append(f"'{field_name}' is required")
        
        if errors:
            return errors
        
        # Validate child_code format
        child_code = event_data.get('child_code')
        if not isinstance(child_code, str) or len(child_code) == 0 or len(child_code) > 100:
            errors.append("'child_code' must be a non-empty string with max 100 characters")
        
        # Validate puzzle_id format
        puzzle_id = event_data.get('puzzle_id')
        if not isinstance(puzzle_id, str) or len(puzzle_id) == 0 or len(puzzle_id) > 100:
            errors.append("'puzzle_id' must be a non-empty string with max 100 characters")
        
        # Validate skill_tags
        skill_tags = event_data.get('skill_tags')
        if not isinstance(skill_tags, list) or len(skill_tags) == 0:
            errors.append("'skill_tags' must be a non-empty list")
        elif not all(tag in VALID_SKILL_TAGS for tag in skill_tags):
            errors.append(f"'skill_tags' must contain only valid tags: {VALID_SKILL_TAGS}")
        
        # Validate timestamps
        started_at = event_data.get('started_at')
        ended_at = event_data.get('ended_at')
        
        # Parse timestamps if they are strings
        if isinstance(started_at, str):
            try:
                started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                errors.append("'started_at' must be a valid ISO datetime string")
                started_at = None
        
        if isinstance(ended_at, str):
            try:
                ended_at = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                errors.append("'ended_at' must be a valid ISO datetime string")
                ended_at = None
        
        # Check timestamp types
        if started_at is not None and not isinstance(started_at, datetime):
            errors.append("'started_at' must be a datetime")
        if ended_at is not None and not isinstance(ended_at, datetime):
            errors.append("'ended_at' must be a datetime")
        
        # Check timestamp order
        if isinstance(started_at, datetime) and isinstance(ended_at, datetime):
            if ended_at < started_at:
                errors.append("'ended_at' must be after 'started_at'")
        
        # Validate completed
        completed = event_data.get('completed')
        if not isinstance(completed, bool):
            errors.append("'completed' must be a boolean")
        
        return errors
    
    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        """Parse a datetime value from string or datetime object."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                return None
        return None
    
    @staticmethod
    def ingest_events(events_data: list[dict]) -> IngestResult:
        """Ingest a batch of events.
        
        Args:
            events_data: List of event dictionaries
            
        Returns:
            IngestResult with counts and any errors
        """
        result = IngestResult(total_received=len(events_data))
        
        events_to_add = []
        
        for index, event_data in enumerate(events_data):
            # Validate the event
            validation_errors = EventService.validate_event(event_data)
            
            if validation_errors:
                result.total_rejected += 1
                result.errors.append({
                    'index': index,
                    'errors': validation_errors
                })
                continue
            
            # Parse timestamps
            started_at = EventService._parse_datetime(event_data['started_at'])
            ended_at = EventService._parse_datetime(event_data['ended_at'])
            
            # Create event instance
            event = EventRaw(
                child_code=event_data['child_code'],
                puzzle_id=event_data['puzzle_id'],
                skill_tags=event_data['skill_tags'],
                started_at=started_at,
                ended_at=ended_at,
                completed=event_data['completed']
            )
            
            events_to_add.append(event)
            result.total_accepted += 1
        
        # Batch insert all valid events
        if events_to_add:
            db.session.add_all(events_to_add)
            db.session.commit()
        
        return result
    
    @staticmethod
    def get_events_by_child_code(child_code: str) -> list[EventRaw]:
        """Get all events for a specific child code.
        
        Args:
            child_code: The pseudonymous child identifier
            
        Returns:
            List of EventRaw instances
        """
        return EventRaw.query.filter_by(child_code=child_code).all()
    
    @staticmethod
    def verify_child_code_exists(child_code: str) -> bool:
        """Check if a child with the given code exists.
        
        Args:
            child_code: The pseudonymous child identifier
            
        Returns:
            True if child exists, False otherwise
        """
        return Child.query.filter_by(child_code=child_code).first() is not None
