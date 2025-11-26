"""Database models package.

This module provides SQLAlchemy models for the educational platform.
All models are imported here for convenient access and to ensure
they are registered with SQLAlchemy before table creation.
"""
from app import db

# Import all models to register them with SQLAlchemy
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.consent import ParentLink
from app.models.event import EventRaw
from app.models.metrics import ChildDailyMetrics, ClassWeeklyMetrics, SchoolWeeklyMetrics
from app.models.template import ActivitySuggestion, MessageTemplate

__all__ = [
    'db',
    'School',
    'Teacher',
    'Class',
    'Child',
    'ParentLink',
    'EventRaw',
    'ChildDailyMetrics',
    'ClassWeeklyMetrics',
    'SchoolWeeklyMetrics',
    'ActivitySuggestion',
    'MessageTemplate',
]
