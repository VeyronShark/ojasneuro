"""Marshmallow schemas for Child model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
Requirements: 9.3 - Pseudonymous child identifiers for privacy
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.child import Child


class ChildSchema(BaseSchema):
    """Schema for Child model serialization/deserialization.
    
    Note: child_code is the pseudonymous identifier used in events.
    """
    
    id = fields.Integer(dump_only=True)
    class_id = fields.Integer(required=True)
    display_name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    child_code = fields.String(dump_only=True)  # Auto-generated, read-only
    age = fields.Integer(allow_none=True, validate=validate.Range(min=0, max=18))
    
    # Nested relationships (optional)
    class_ = fields.Nested('ClassSchema', dump_only=True, only=['id', 'name', 'grade_level'])
    
    @post_load
    def make_child(self, data, **kwargs):
        """Create Child instance from validated data."""
        return Child(**data)


class ChildListSchema(BaseSchema):
    """Schema for child list response (minimal fields)."""
    
    id = fields.Integer()
    display_name = fields.String()
    child_code = fields.String()
    age = fields.Integer(allow_none=True)


class ChildDetailSchema(BaseSchema):
    """Schema for detailed child response with metrics."""
    
    id = fields.Integer()
    class_id = fields.Integer()
    display_name = fields.String()
    child_code = fields.String()
    age = fields.Integer(allow_none=True)
    class_ = fields.Nested('ClassSchema', only=['id', 'name', 'grade_level'])
    consent_status = fields.String(allow_none=True)
