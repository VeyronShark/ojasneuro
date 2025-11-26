"""Marshmallow schemas for Metrics models.

Requirements: 10.1, 10.2, 10.3 - JSON serialization/deserialization with round-trip consistency
Requirements: 4.1, 4.2 - Class and child metrics responses
"""
from marshmallow import fields, post_load

from app.schemas import BaseSchema
from app.models.metrics import ChildDailyMetrics, ClassWeeklyMetrics, SchoolWeeklyMetrics


class SkillScoresSchema(BaseSchema):
    """Schema for skill scores dictionary."""
    
    attention = fields.Float(allow_none=True)
    patience = fields.Float(allow_none=True)
    sensory = fields.Float(allow_none=True)
    emotionAwareness = fields.Float(allow_none=True)
    bodyAwareness = fields.Float(allow_none=True)


class ChildDailyMetricsSchema(BaseSchema):
    """Schema for ChildDailyMetrics model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    child_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    sessions_count = fields.Integer(load_default=0)
    avg_duration = fields.Integer(allow_none=True)  # in seconds
    skill_scores = fields.Dict(keys=fields.String(), values=fields.Float(), allow_none=True)
    
    @post_load
    def make_metrics(self, data, **kwargs):
        """Create ChildDailyMetrics instance from validated data."""
        return ChildDailyMetrics(**data)


class ChildMetricsResponseSchema(BaseSchema):
    """Schema for child metrics API response."""
    
    child_id = fields.Integer()
    child_code = fields.String()
    display_name = fields.String()
    date_range = fields.Dict(keys=fields.String(), values=fields.Date())
    total_sessions = fields.Integer()
    avg_duration_seconds = fields.Float()
    skill_scores = fields.Dict(keys=fields.String(), values=fields.Float())
    daily_metrics = fields.List(fields.Nested(ChildDailyMetricsSchema))


class SkillProfileSchema(BaseSchema):
    """Schema for child skill profile response."""
    
    child_id = fields.Integer()
    attention = fields.Float(allow_none=True)
    patience = fields.Float(allow_none=True)
    sensory = fields.Float(allow_none=True)
    emotionAwareness = fields.Float(allow_none=True)
    bodyAwareness = fields.Float(allow_none=True)
    last_updated = fields.DateTime(allow_none=True)


class ClassWeeklyMetricsSchema(BaseSchema):
    """Schema for ClassWeeklyMetrics model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    class_id = fields.Integer(required=True)
    week_start_date = fields.Date(required=True)
    engagement_level = fields.String(allow_none=True)
    avg_skill_scores = fields.Dict(keys=fields.String(), values=fields.Float(), allow_none=True)
    
    @post_load
    def make_metrics(self, data, **kwargs):
        """Create ClassWeeklyMetrics instance from validated data."""
        return ClassWeeklyMetrics(**data)


class ClassMetricsResponseSchema(BaseSchema):
    """Schema for class metrics API response."""
    
    class_id = fields.Integer()
    class_name = fields.String()
    date_range = fields.Dict(keys=fields.String(), values=fields.Date())
    total_children = fields.Integer()
    active_children = fields.Integer()
    total_sessions = fields.Integer()
    avg_sessions_per_child = fields.Float()
    engagement_level = fields.String()
    avg_skill_scores = fields.Dict(keys=fields.String(), values=fields.Float())


class ClassSkillOverviewSchema(BaseSchema):
    """Schema for class skill distribution overview."""
    
    class_id = fields.Integer()
    skill_distributions = fields.Dict(
        keys=fields.String(),
        values=fields.Dict(keys=fields.String(), values=fields.Float())
    )
    class_averages = fields.Dict(keys=fields.String(), values=fields.Float())


class SchoolWeeklyMetricsSchema(BaseSchema):
    """Schema for SchoolWeeklyMetrics model serialization/deserialization."""
    
    id = fields.Integer(dump_only=True)
    school_id = fields.Integer(required=True)
    week_start_date = fields.Date(required=True)
    metrics = fields.Dict(allow_none=True)
    
    @post_load
    def make_metrics(self, data, **kwargs):
        """Create SchoolWeeklyMetrics instance from validated data."""
        return SchoolWeeklyMetrics(**data)


class DateRangeSchema(BaseSchema):
    """Schema for date range query parameters."""
    
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
