"""Marshmallow schemas for Consent/ParentLink model.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
Requirements: 7.1, 7.2 - Consent submission and status retrieval
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.consent import ParentLink


class ParentLinkSchema(BaseSchema):
    """Schema for ParentLink model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    child_id = fields.Integer(required=True)
    parent_id = fields.Integer(required=True)
    consent_status = fields.String(
        load_default='pending',
        validate=validate.OneOf(['pending', 'granted', 'denied'])
    )
    consent_timestamp = fields.DateTime(allow_none=True)
    consent_scope = fields.String(allow_none=True, validate=validate.Length(max=100))
    
    @post_load
    def make_parent_link(self, data, **kwargs):
        """Create ParentLink instance from validated data."""
        return ParentLink(**data)


class ConsentSubmitSchema(BaseSchema):
    """Schema for consent submission request."""
    
    child_id = fields.Integer(required=True)
    parent_id = fields.Integer(required=True)
    consent_status = fields.String(
        required=True,
        validate=validate.OneOf(['granted', 'denied'])
    )
    scope = fields.String(
        load_default='full',
        validate=validate.OneOf(['full', 'limited', 'analytics_only'])
    )


class ConsentStatusSchema(BaseSchema):
    """Schema for consent status response."""
    
    child_id = fields.Integer()
    consent_status = fields.String()
    consent_timestamp = fields.DateTime(allow_none=True)
    consent_scope = fields.String(allow_none=True)
    is_consent_granted = fields.Boolean()
