"""Marshmallow schemas for Event model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
Requirements: 3.1 - Event validation (child_id, puzzle_id, skill_tags, timestamps, completion_status)
Requirements: 9.3 - Events contain only pseudonymous identifiers
"""
from marshmallow import fields, post_load, validate, validates_schema, ValidationError

from app.schemas import BaseSchema
from app.models.event import EventRaw


# Valid skill tags for the platform
VALID_SKILL_TAGS = ['attention', 'patience', 'sensory', 'emotionAwareness', 'bodyAwareness']


class EventInputSchema(BaseSchema):
    """Schema for event ingestion request validation.
    
    Validates all required fields per Requirements 3.1.
    """
    
    child_code = fields.String(required=True, validate=validate.Length(min=1, max=100))
    puzzle_id = fields.String(required=True, validate=validate.Length(min=1, max=100))
    skill_tags = fields.List(
        fields.String(validate=validate.OneOf(VALID_SKILL_TAGS)),
        required=True,
        validate=validate.Length(min=1)
    )
    started_at = fields.DateTime(required=True)
    ended_at = fields.DateTime(required=True)
    completed = fields.Boolean(required=True)
    
    @validates_schema
    def validate_timestamps(self, data, **kwargs):
        """Ensure ended_at is after started_at."""
        if 'started_at' in data and 'ended_at' in data:
            if data['ended_at'] < data['started_at']:
                raise ValidationError('ended_at must be after started_at', 'ended_at')
    
    @post_load
    def make_event(self, data, **kwargs):
        """Create EventRaw instance from validated data."""
        return EventRaw(**data)


class EventOutputSchema(BaseSchema):
    """Schema for event response serialization.
    
    Note: Only child_code is included, never PII (Requirements 9.3).
    """
    
    id = fields.Integer()
    child_code = fields.String()
    puzzle_id = fields.String()
    skill_tags = fields.List(fields.String())
    started_at = fields.DateTime()
    ended_at = fields.DateTime()
    completed = fields.Boolean()
    duration_seconds = fields.Float(dump_only=True)


class EventBatchInputSchema(BaseSchema):
    """Schema for batch event ingestion."""
    
    events = fields.List(
        fields.Nested(EventInputSchema),
        required=True,
        validate=validate.Length(min=1, max=1000)
    )


class EventIngestResultSchema(BaseSchema):
    """Schema for event ingestion result response."""
    
    total_received = fields.Integer()
    total_accepted = fields.Integer()
    total_rejected = fields.Integer()
    errors = fields.List(fields.Dict())
