"""Metrics models for aggregated analytics data.

Requirements: 4.1 - Class metrics aggregation.
Requirements: 4.2 - Child metrics computation.
"""
from app import db


class ChildDailyMetrics(db.Model):
    """Aggregated daily metrics for a child.
    
    Stores pre-computed metrics derived from raw events.
    """
    __tablename__ = 'child_daily_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sessions_count = db.Column(db.Integer, default=0)
    avg_duration = db.Column(db.Integer)  # in seconds
    skill_scores = db.Column(db.JSON)  # Dict of skill_tag -> score
    
    # Relationships
    child = db.relationship('Child', back_populates='daily_metrics')
    
    # Unique constraint on child_id + date
    __table_args__ = (
        db.UniqueConstraint('child_id', 'date', name='uq_child_daily_metrics'),
    )
    
    def __repr__(self):
        return f'<ChildDailyMetrics child={self.child_id} date={self.date}>'
    
    def to_dict(self):
        """Serialize metrics to dictionary for JSON response."""
        return {
            'id': self.id,
            'child_id': self.child_id,
            'date': self.date.isoformat() if self.date else None,
            'sessions_count': self.sessions_count,
            'avg_duration': self.avg_duration,
            'skill_scores': self.skill_scores,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a ChildDailyMetrics instance from a dictionary."""
        from datetime import date as date_type
        
        date_val = data.get('date')
        if isinstance(date_val, str):
            date_val = date_type.fromisoformat(date_val)
        
        return cls(
            id=data.get('id'),
            child_id=data.get('child_id'),
            date=date_val,
            sessions_count=data.get('sessions_count', 0),
            avg_duration=data.get('avg_duration'),
            skill_scores=data.get('skill_scores'),
        )


class ClassWeeklyMetrics(db.Model):
    """Aggregated weekly metrics for a class.
    
    Stores pre-computed class-level engagement and skill data.
    """
    __tablename__ = 'class_weekly_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    engagement_level = db.Column(db.String(20))  # 'low', 'medium', 'high'
    avg_skill_scores = db.Column(db.JSON)  # Dict of skill_tag -> avg score
    
    # Relationships
    class_ = db.relationship('Class', back_populates='weekly_metrics')
    
    # Unique constraint on class_id + week_start_date
    __table_args__ = (
        db.UniqueConstraint('class_id', 'week_start_date', name='uq_class_weekly_metrics'),
    )
    
    def __repr__(self):
        return f'<ClassWeeklyMetrics class={self.class_id} week={self.week_start_date}>'
    
    def to_dict(self):
        """Serialize metrics to dictionary for JSON response."""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'week_start_date': self.week_start_date.isoformat() if self.week_start_date else None,
            'engagement_level': self.engagement_level,
            'avg_skill_scores': self.avg_skill_scores,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a ClassWeeklyMetrics instance from a dictionary."""
        from datetime import date as date_type
        
        week_start = data.get('week_start_date')
        if isinstance(week_start, str):
            week_start = date_type.fromisoformat(week_start)
        
        return cls(
            id=data.get('id'),
            class_id=data.get('class_id'),
            week_start_date=week_start,
            engagement_level=data.get('engagement_level'),
            avg_skill_scores=data.get('avg_skill_scores'),
        )


class SchoolWeeklyMetrics(db.Model):
    """Aggregated weekly metrics for a school.
    
    Stores pre-computed school-wide engagement and skill data.
    """
    __tablename__ = 'school_weekly_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    metrics = db.Column(db.JSON)  # Flexible metrics storage
    
    # Relationships
    school = db.relationship('School', back_populates='weekly_metrics')
    
    # Unique constraint on school_id + week_start_date
    __table_args__ = (
        db.UniqueConstraint('school_id', 'week_start_date', name='uq_school_weekly_metrics'),
    )
    
    def __repr__(self):
        return f'<SchoolWeeklyMetrics school={self.school_id} week={self.week_start_date}>'
    
    def to_dict(self):
        """Serialize metrics to dictionary for JSON response."""
        return {
            'id': self.id,
            'school_id': self.school_id,
            'week_start_date': self.week_start_date.isoformat() if self.week_start_date else None,
            'metrics': self.metrics,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a SchoolWeeklyMetrics instance from a dictionary."""
        from datetime import date as date_type
        
        week_start = data.get('week_start_date')
        if isinstance(week_start, str):
            week_start = date_type.fromisoformat(week_start)
        
        return cls(
            id=data.get('id'),
            school_id=data.get('school_id'),
            week_start_date=week_start,
            metrics=data.get('metrics'),
        )
