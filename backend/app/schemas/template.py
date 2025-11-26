"""Marshmallow schemas for Template models.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
Requirements: 5.3, 8.1 - Activity suggestions and message templates
"""
from marshmallow import fields, post_load, validate

from app.schemas import BaseSchema
from app.models.template import ActivitySuggestion, MessageTemplate


# Valid skill tags for activity suggestions
VALID_SKILL_TAGS = ['attention', 'patience', 'sensory', 'emotionAwareness', 'bodyAwareness']


class ActivitySuggestionSchema(BaseSchema):
    """Schema for ActivitySuggestion model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    skill_tag = fields.String(
        required=True,
        validate=validate.OneOf(VALID_SKILL_TAGS)
    )
    activity_text = fields.String(required=True, validate=validate.Length(min=1))
    
    @post_load
    def make_suggestion(self, data, **kwargs):
        """Create ActivitySuggestion instance from validated data."""
        return ActivitySuggestion(**data)


class ActivitySuggestionListSchema(BaseSchema):
    """Schema for activity suggestions list response."""
    
    skill_tag = fields.String()
    suggestions = fields.List(fields.String())


class MessageTemplateSchema(BaseSchema):
    """Schema for MessageTemplate model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    template_type = fields.String(
        required=True,
        validate=validate.OneOf(['parent_message', 'handout', 'welcome', 'report_intro'])
    )
    language = fields.String(load_default='en', validate=validate.Length(min=2, max=10))
    content = fields.String(required=True, validate=validate.Length(min=1))
    
    @post_load
    def make_template(self, data, **kwargs):
        """Create MessageTemplate instance from validated data."""
        return MessageTemplate(**data)


class TemplateRequestSchema(BaseSchema):
    """Schema for template retrieval request parameters."""
    
    template_type = fields.String(required=True)
    language = fields.String(load_default='en')


class TemplateResponseSchema(BaseSchema):
    """Schema for template response."""
    
    template_type = fields.String()
    language = fields.String()
    content = fields.String()
