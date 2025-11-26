"""Marshmallow schemas for Class model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.class_ import Class


class ClassSchema(BaseSchema):
    """Schema for Class model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    school_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    grade_level = fields.String(allow_none=True, validate=validate.Length(max=50))
    primary_teacher_id = fields.Integer(allow_none=True)
    
    # Nested relationships (optional)
    primary_teacher = fields.Nested('TeacherSchema', dump_only=True, only=['id', 'name', 'email'])
    children = fields.List(fields.Nested('ChildSchema'), dump_only=True)
    
    @post_load
    def make_class(self, data, **kwargs):
        """Create Class instance from validated data."""
        return Class(**data)


class ClassListSchema(BaseSchema):
    """Schema for class list response (minimal fields)."""
    
    id = fields.Integer()
    name = fields.String()
    grade_level = fields.String(allow_none=True)
    primary_teacher_id = fields.Integer(allow_none=True)
    children_count = fields.Integer()
