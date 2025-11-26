"""Marshmallow schemas for Teacher model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.teacher import Teacher


class TeacherSchema(BaseSchema):
    """Schema for Teacher model serialization/deserialization.
    
    Note: password_hash is never serialized for security.
    Password is write-only for creating/updating teachers.
    """
    
    id = fields.Integer(dump_only=True)
    school_id = fields.Integer(required=True)
    email = fields.Email(required=True)
    password = fields.String(load_only=True, validate=validate.Length(min=8))
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    role = fields.String(
        required=True,
        validate=validate.OneOf(['teacher', 'admin'])
    )
    
    # Nested relationships (optional)
    school = fields.Nested('SchoolSchema', dump_only=True)
    
    @post_load
    def make_teacher(self, data, **kwargs):
        """Create Teacher instance from validated data."""
        password = data.pop('password', None)
        teacher = Teacher(**data)
        if password:
            teacher.set_password(password)
        return teacher


class TeacherProfileSchema(BaseSchema):
    """Schema for teacher profile response (used in /me endpoint)."""
    
    id = fields.Integer()
    school_id = fields.Integer()
    email = fields.Email()
    name = fields.String()
    role = fields.String()
    school = fields.Nested('SchoolSchema', only=['id', 'name'])


class LoginRequestSchema(BaseSchema):
    """Schema for login request validation."""
    
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class LoginResponseSchema(BaseSchema):
    """Schema for login response."""
    
    access_token = fields.String(required=True)
    token_type = fields.String(dump_default='Bearer')
    user = fields.Nested(TeacherProfileSchema)
