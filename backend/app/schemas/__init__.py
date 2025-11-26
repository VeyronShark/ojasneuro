"""Marshmallow schemas package.

This module provides Marshmallow schemas for serialization and validation
of API request/response data.

Requirements: 10.1, 10.2 - JSON serialization and deserialization
"""
from marshmallow import Schema, fields, validate, post_load, ValidationError, EXCLUDE


class BaseSchema(Schema):
    """Base schema with common configuration for all schemas.
    
    Provides consistent behavior across all API schemas:
    - Unknown fields are excluded (not rejected)
    - Consistent date/datetime formatting
    """
    
    class Meta:
        # Exclude unknown fields instead of raising errors
        unknown = EXCLUDE
        # Use ISO format for dates/datetimes
        datetimeformat = '%Y-%m-%dT%H:%M:%S'
        dateformat = '%Y-%m-%d'


class PaginatedSchema(Schema):
    """Schema for paginated response wrapper.
    
    Used to wrap list responses with pagination metadata.
    """
    page = fields.Integer(dump_default=1)
    per_page = fields.Integer(dump_default=20)
    total = fields.Integer()
    total_pages = fields.Integer()
    items = fields.List(fields.Dict())  # Override in subclasses with specific schema


class ErrorDetailSchema(Schema):
    """Schema for individual error details."""
    field = fields.String()
    message = fields.String(required=True)


class ErrorResponseSchema(Schema):
    """Schema for API error responses.
    
    Provides consistent error format across all endpoints.
    """
    code = fields.String(required=True)
    message = fields.String(required=True)
    details = fields.List(fields.Nested(ErrorDetailSchema))


# Import entity schemas after base classes are defined
from app.schemas.school import SchoolSchema, SchoolSummarySchema
from app.schemas.teacher import (
    TeacherSchema, TeacherProfileSchema,
    LoginRequestSchema, LoginResponseSchema
)
from app.schemas.class_ import ClassSchema, ClassListSchema
from app.schemas.child import ChildSchema, ChildListSchema, ChildDetailSchema
from app.schemas.event import (
    EventInputSchema, EventOutputSchema,
    EventBatchInputSchema, EventIngestResultSchema,
    VALID_SKILL_TAGS
)
from app.schemas.metrics import (
    ChildDailyMetricsSchema, ChildMetricsResponseSchema, SkillProfileSchema,
    ClassWeeklyMetricsSchema, ClassMetricsResponseSchema, ClassSkillOverviewSchema,
    SchoolWeeklyMetricsSchema, DateRangeSchema
)
from app.schemas.consent import (
    ParentLinkSchema, ConsentSubmitSchema, ConsentStatusSchema
)
from app.schemas.template import (
    ActivitySuggestionSchema, ActivitySuggestionListSchema,
    MessageTemplateSchema, TemplateRequestSchema, TemplateResponseSchema
)


# Re-export all schemas for convenient access
__all__ = [
    # Base utilities
    'Schema',
    'fields',
    'validate',
    'post_load',
    'ValidationError',
    'EXCLUDE',
    'BaseSchema',
    'PaginatedSchema',
    'ErrorDetailSchema',
    'ErrorResponseSchema',
    
    # School schemas
    'SchoolSchema',
    'SchoolSummarySchema',
    
    # Teacher schemas
    'TeacherSchema',
    'TeacherProfileSchema',
    'LoginRequestSchema',
    'LoginResponseSchema',
    
    # Class schemas
    'ClassSchema',
    'ClassListSchema',
    
    # Child schemas
    'ChildSchema',
    'ChildListSchema',
    'ChildDetailSchema',
    
    # Event schemas
    'EventInputSchema',
    'EventOutputSchema',
    'EventBatchInputSchema',
    'EventIngestResultSchema',
    'VALID_SKILL_TAGS',
    
    # Metrics schemas
    'ChildDailyMetricsSchema',
    'ChildMetricsResponseSchema',
    'SkillProfileSchema',
    'ClassWeeklyMetricsSchema',
    'ClassMetricsResponseSchema',
    'ClassSkillOverviewSchema',
    'SchoolWeeklyMetricsSchema',
    'DateRangeSchema',
    
    # Consent schemas
    'ParentLinkSchema',
    'ConsentSubmitSchema',
    'ConsentStatusSchema',
    
    # Template schemas
    'ActivitySuggestionSchema',
    'ActivitySuggestionListSchema',
    'MessageTemplateSchema',
    'TemplateRequestSchema',
    'TemplateResponseSchema',
]
