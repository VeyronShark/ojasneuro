"""Analytics service for computing metrics and skill scores.

Requirements: 4.1 - Class metrics aggregation with date range filtering
Requirements: 4.2 - Child metrics computation (sessions count, avg duration, skill scores)
Requirements: 4.3 - Child skill profile with scores for each skill tag
Requirements: 4.4 - Class skill overview with aggregated distributions
Requirements: 4.5 - Metrics derived from raw events using skill mapping rules
"""
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional
from collections import defaultdict

from sqlalchemy import func

from app import db
from app.models.event import EventRaw
from app.models.child import Child
from app.models.class_ import Class
from app.models.metrics import ChildDailyMetrics, ClassWeeklyMetrics
from app.schemas.event import VALID_SKILL_TAGS


class ChildNotFoundError(Exception):
    """Raised when a child is not found."""
    pass


class ClassNotFoundError(Exception):
    """Raised when a class is not found."""
    pass


@dataclass
class DateRange:
    """Represents a date range for filtering metrics."""
    start_date: date
    end_date: date
    
    def to_dict(self) -> dict:
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }


@dataclass
class SkillProfile:
    """Skill scores for a child across all skill tags."""
    child_id: int
    attention: Optional[float] = None
    patience: Optional[float] = None
    sensory: Optional[float] = None
    emotionAwareness: Optional[float] = None
    bodyAwareness: Optional[float] = None
    last_updated: Optional[datetime] = None

    
    def to_dict(self) -> dict:
        return {
            'child_id': self.child_id,
            'attention': self.attention,
            'patience': self.patience,
            'sensory': self.sensory,
            'emotionAwareness': self.emotionAwareness,
            'bodyAwareness': self.bodyAwareness,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_scores_dict(cls, child_id: int, scores: dict, last_updated: datetime = None) -> 'SkillProfile':
        """Create a SkillProfile from a dictionary of scores."""
        return cls(
            child_id=child_id,
            attention=scores.get('attention'),
            patience=scores.get('patience'),
            sensory=scores.get('sensory'),
            emotionAwareness=scores.get('emotionAwareness'),
            bodyAwareness=scores.get('bodyAwareness'),
            last_updated=last_updated
        )


@dataclass
class ChildMetrics:
    """Aggregated metrics for a child over a date range."""
    child_id: int
    child_code: str
    display_name: str
    date_range: DateRange
    total_sessions: int = 0
    avg_duration_seconds: float = 0.0
    skill_scores: dict = field(default_factory=dict)
    daily_metrics: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'child_id': self.child_id,
            'child_code': self.child_code,
            'display_name': self.display_name,
            'date_range': self.date_range.to_dict(),
            'total_sessions': self.total_sessions,
            'avg_duration_seconds': self.avg_duration_seconds,
            'skill_scores': self.skill_scores,
            'daily_metrics': [m.to_dict() if hasattr(m, 'to_dict') else m for m in self.daily_metrics]
        }


@dataclass
class ClassMetrics:
    """Aggregated metrics for a class over a date range."""
    class_id: int
    class_name: str
    date_range: DateRange
    total_children: int = 0
    active_children: int = 0
    total_sessions: int = 0
    avg_sessions_per_child: float = 0.0
    engagement_level: str = 'low'
    avg_skill_scores: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'date_range': self.date_range.to_dict(),
            'total_children': self.total_children,
            'active_children': self.active_children,
            'total_sessions': self.total_sessions,
            'avg_sessions_per_child': self.avg_sessions_per_child,
            'engagement_level': self.engagement_level,
            'avg_skill_scores': self.avg_skill_scores
        }


@dataclass
class ClassSkillOverview:
    """Skill distribution overview for a class."""
    class_id: int
    skill_distributions: dict = field(default_factory=dict)
    class_averages: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'class_id': self.class_id,
            'skill_distributions': self.skill_distributions,
            'class_averages': self.class_averages
        }


class AnalyticsService:
    """Service for computing analytics and metrics from events."""
    
    @staticmethod
    def _compute_skill_scores_from_events(events: list[EventRaw]) -> dict:
        """Compute skill scores from a list of events.
        
        Skill scores are computed as the percentage of completed puzzles
        for each skill tag.
        
        Args:
            events: List of EventRaw instances
            
        Returns:
            Dictionary mapping skill tags to scores (0.0 to 100.0)
        """
        if not events:
            return {}
        
        skill_counts = defaultdict(lambda: {'completed': 0, 'total': 0})
        
        for event in events:
            for skill_tag in event.skill_tags:
                skill_counts[skill_tag]['total'] += 1
                if event.completed:
                    skill_counts[skill_tag]['completed'] += 1
        
        scores = {}
        for skill_tag in VALID_SKILL_TAGS:
            if skill_tag in skill_counts and skill_counts[skill_tag]['total'] > 0:
                # Convert to percentage (0-100)
                scores[skill_tag] = round((skill_counts[skill_tag]['completed'] / skill_counts[skill_tag]['total']) * 100, 1)
            else:
                scores[skill_tag] = None
        
        return scores

    
    @staticmethod
    def _compute_avg_duration(events: list[EventRaw]) -> float:
        """Compute average duration in seconds from events.
        
        Args:
            events: List of EventRaw instances
            
        Returns:
            Average duration in seconds, or 0.0 if no events
        """
        if not events:
            return 0.0
        
        total_duration = sum(event.duration_seconds for event in events)
        return total_duration / len(events)
    
    @staticmethod
    def _determine_engagement_level(avg_sessions_per_child: float) -> str:
        """Determine engagement level based on average sessions per child.
        
        Args:
            avg_sessions_per_child: Average number of sessions per child
            
        Returns:
            'low', 'medium', or 'high'
        """
        if avg_sessions_per_child >= 5:
            return 'high'
        elif avg_sessions_per_child >= 2:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_child_metrics(child_id: int, date_range: DateRange) -> ChildMetrics:
        """Get aggregated metrics for a child over a date range.
        
        Args:
            child_id: ID of the child
            date_range: DateRange for filtering events
            
        Returns:
            ChildMetrics with aggregated data
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        child = db.session.get(Child, child_id)
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Get events for this child within the date range
        events = EventRaw.query.filter(
            EventRaw.child_code == child.child_code,
            func.date(EventRaw.started_at) >= date_range.start_date,
            func.date(EventRaw.started_at) <= date_range.end_date
        ).all()
        
        # Compute metrics
        total_sessions = len(events)
        avg_duration = AnalyticsService._compute_avg_duration(events)
        skill_scores = AnalyticsService._compute_skill_scores_from_events(events)
        
        # Get or compute daily metrics
        daily_metrics = ChildDailyMetrics.query.filter(
            ChildDailyMetrics.child_id == child_id,
            ChildDailyMetrics.date >= date_range.start_date,
            ChildDailyMetrics.date <= date_range.end_date
        ).all()
        
        return ChildMetrics(
            child_id=child.id,
            child_code=child.child_code,
            display_name=child.display_name,
            date_range=date_range,
            total_sessions=total_sessions,
            avg_duration_seconds=avg_duration,
            skill_scores=skill_scores,
            daily_metrics=daily_metrics
        )
    
    @staticmethod
    def get_skill_profile(child_id: int) -> SkillProfile:
        """Get skill profile for a child based on all their events.
        
        Args:
            child_id: ID of the child
            
        Returns:
            SkillProfile with scores for each skill tag
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        child = db.session.get(Child, child_id)
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Get all events for this child
        events = EventRaw.query.filter_by(child_code=child.child_code).all()
        
        # Compute skill scores
        scores = AnalyticsService._compute_skill_scores_from_events(events)
        
        # Get last event timestamp
        last_event = EventRaw.query.filter_by(child_code=child.child_code).order_by(
            EventRaw.ended_at.desc()
        ).first()
        last_updated = last_event.ended_at if last_event else None
        
        return SkillProfile.from_scores_dict(child_id, scores, last_updated)

    
    @staticmethod
    def get_class_metrics(class_id: int, date_range: DateRange) -> ClassMetrics:
        """Get aggregated metrics for a class over a date range.
        
        Args:
            class_id: ID of the class
            date_range: DateRange for filtering events
            
        Returns:
            ClassMetrics with aggregated data
            
        Raises:
            ClassNotFoundError: If class doesn't exist
        """
        class_obj = db.session.get(Class, class_id)
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        # Get all children in the class
        children = Child.query.filter_by(class_id=class_id).all()
        total_children = len(children)
        
        if total_children == 0:
            return ClassMetrics(
                class_id=class_id,
                class_name=class_obj.name,
                date_range=date_range,
                total_children=0,
                active_children=0,
                total_sessions=0,
                avg_sessions_per_child=0.0,
                engagement_level='low',
                avg_skill_scores={}
            )
        
        # Get child codes for all children in the class
        child_codes = [child.child_code for child in children]
        
        # Get all events for children in this class within the date range
        events = EventRaw.query.filter(
            EventRaw.child_code.in_(child_codes),
            func.date(EventRaw.started_at) >= date_range.start_date,
            func.date(EventRaw.started_at) <= date_range.end_date
        ).all()
        
        # Count active children (those with at least one event)
        active_child_codes = set(event.child_code for event in events)
        active_children = len(active_child_codes)
        
        # Compute total sessions
        total_sessions = len(events)
        
        # Compute average sessions per child
        avg_sessions_per_child = total_sessions / total_children if total_children > 0 else 0.0
        
        # Determine engagement level
        engagement_level = AnalyticsService._determine_engagement_level(avg_sessions_per_child)
        
        # Compute average skill scores across all events
        avg_skill_scores = AnalyticsService._compute_skill_scores_from_events(events)
        
        return ClassMetrics(
            class_id=class_id,
            class_name=class_obj.name,
            date_range=date_range,
            total_children=total_children,
            active_children=active_children,
            total_sessions=total_sessions,
            avg_sessions_per_child=avg_sessions_per_child,
            engagement_level=engagement_level,
            avg_skill_scores=avg_skill_scores
        )
    
    @staticmethod
    def get_class_skill_overview(class_id: int) -> ClassSkillOverview:
        """Get skill distribution overview for a class.
        
        Args:
            class_id: ID of the class
            
        Returns:
            ClassSkillOverview with skill distributions and averages
            
        Raises:
            ClassNotFoundError: If class doesn't exist
        """
        class_obj = db.session.get(Class, class_id)
        if class_obj is None:
            raise ClassNotFoundError(f"Class with id {class_id} not found")
        
        # Get all children in the class
        children = Child.query.filter_by(class_id=class_id).all()
        
        if not children:
            return ClassSkillOverview(
                class_id=class_id,
                skill_distributions={},
                class_averages={}
            )
        
        # Compute skill profile for each child
        child_skill_scores = []
        for child in children:
            events = EventRaw.query.filter_by(child_code=child.child_code).all()
            if events:
                scores = AnalyticsService._compute_skill_scores_from_events(events)
                child_skill_scores.append(scores)
        
        if not child_skill_scores:
            return ClassSkillOverview(
                class_id=class_id,
                skill_distributions={},
                class_averages={}
            )
        
        # Compute class averages and distributions
        class_averages = {}
        skill_distributions = {}
        
        for skill_tag in VALID_SKILL_TAGS:
            scores_for_skill = [
                scores[skill_tag] 
                for scores in child_skill_scores 
                if scores.get(skill_tag) is not None
            ]
            
            if scores_for_skill:
                class_averages[skill_tag] = sum(scores_for_skill) / len(scores_for_skill)
                
                # Compute distribution (low, medium, high)
                low_count = sum(1 for s in scores_for_skill if s < 0.33)
                medium_count = sum(1 for s in scores_for_skill if 0.33 <= s < 0.67)
                high_count = sum(1 for s in scores_for_skill if s >= 0.67)
                total = len(scores_for_skill)
                
                skill_distributions[skill_tag] = {
                    'low': low_count / total if total > 0 else 0,
                    'medium': medium_count / total if total > 0 else 0,
                    'high': high_count / total if total > 0 else 0
                }
            else:
                class_averages[skill_tag] = None
                skill_distributions[skill_tag] = {'low': 0, 'medium': 0, 'high': 0}
        
        return ClassSkillOverview(
            class_id=class_id,
            skill_distributions=skill_distributions,
            class_averages=class_averages
        )
    
    @staticmethod
    def compute_daily_metrics(child_id: int, target_date: date) -> ChildDailyMetrics:
        """Compute and store daily metrics for a child.
        
        Args:
            child_id: ID of the child
            target_date: Date to compute metrics for
            
        Returns:
            ChildDailyMetrics instance (created or updated)
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        child = db.session.get(Child, child_id)
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Get events for this child on the target date
        events = EventRaw.query.filter(
            EventRaw.child_code == child.child_code,
            func.date(EventRaw.started_at) == target_date
        ).all()
        
        # Compute metrics
        sessions_count = len(events)
        avg_duration = int(AnalyticsService._compute_avg_duration(events)) if events else None
        skill_scores = AnalyticsService._compute_skill_scores_from_events(events) if events else None
        
        # Check if metrics already exist for this child and date
        existing_metrics = ChildDailyMetrics.query.filter_by(
            child_id=child_id,
            date=target_date
        ).first()
        
        if existing_metrics:
            # Update existing metrics
            existing_metrics.sessions_count = sessions_count
            existing_metrics.avg_duration = avg_duration
            existing_metrics.skill_scores = skill_scores
            db.session.commit()
            return existing_metrics
        else:
            # Create new metrics
            new_metrics = ChildDailyMetrics(
                child_id=child_id,
                date=target_date,
                sessions_count=sessions_count,
                avg_duration=avg_duration,
                skill_scores=skill_scores
            )
            db.session.add(new_metrics)
            db.session.commit()
            return new_metrics
