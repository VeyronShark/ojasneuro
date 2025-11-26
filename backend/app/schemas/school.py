"""Marshmallow schemas for School model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.school import School


class SchoolSchema(BaseSchema):
    """Schema for School model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    logo = fields.String(allow_none=True, validate=validate.Length(max=50))
    primary_color = fields.String(
        allow_none=True,
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error='Invalid hex color format')
    )
    enrolled_families = fields.Integer(load_default=0, validate=validate.Range(min=0))
    app_installs = fields.Integer(load_default=0, validate=validate.Range(min=0))
    
    @post_load
    def make_school(self, data, **kwargs):
        """Create School instance from validated data."""
        return School(**data)


class SchoolSummarySchema(BaseSchema):
    """Schema for school summary response (includes computed fields)."""
    
    id = fields.Integer()
    name = fields.String()
    logo = fields.String(allow_none=True)
    primary_color = fields.String(allow_none=True)
    enrolled_families = fields.Integer()
    app_installs = fields.Integer()
    total_classes = fields.Integer()
    total_children = fields.Integer()
    total_teachers = fields.Integer()
