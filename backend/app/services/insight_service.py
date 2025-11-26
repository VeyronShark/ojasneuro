"""Insight service for generating child insights and activity suggestions.

Requirements: 5.1 - Generate insight text based on skill scores relative to class averages
Requirements: 5.2 - Include suggested activities when skill score is significantly below class mean
Requirements: 5.3 - Return relevant classroom activities from the suggestion database
"""
from dataclasses import dataclass, field
from typing import Optional
import math

from app import db
from app.models.child import Child
from app.models.template import ActivitySuggestion
from app.services.analytics_service import AnalyticsService, SkillProfile, ClassSkillOverview
from app.schemas.event import VALID_SKILL_TAGS


class ChildNotFoundError(Exception):
    """Raised when a child is not found."""
    pass


class InvalidSkillTagError(Exception):
    """Raised when an invalid skill tag is provided."""
    pass


@dataclass
class Insight:
    """Represents an insight about a child's skill development."""
    skill_tag: str
    child_score: Optional[float]
    class_average: Optional[float]
    deviation: Optional[float]  # How many standard deviations from mean
    insight_text: str
    suggested_activities: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'skill_tag': self.skill_tag,
            'child_score': self.child_score,
            'class_average': self.class_average,
            'deviation': self.deviation,
            'insight_text': self.insight_text,
            'suggested_activities': self.suggested_activities
        }


# Skill tag display names for human-readable insights
SKILL_DISPLAY_NAMES = {
    'attention': 'Attention',
    'patience': 'Patience',
    'sensory': 'Sensory Awareness',
    'emotionAwareness': 'Emotion Awareness',
    'bodyAwareness': 'Body Awareness'
}


class InsightService:
    """Service for generating insights and activity suggestions."""
    
    # Threshold for significant deviation (1 standard deviation)
    SIGNIFICANT_DEVIATION_THRESHOLD = 1.0
    
    @staticmethod
    def _compute_standard_deviation(scores: list[float]) -> float:
        """Compute standard deviation of a list of scores.
        
        Args:
            scores: List of numeric scores
            
        Returns:
            Standard deviation, or 0.0 if insufficient data
        """
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return math.sqrt(variance)
    
    @staticmethod
    def _generate_insight_text(
        skill_tag: str,
        child_score: Optional[float],
        class_average: Optional[float],
        deviation: Optional[float]
    ) -> str:
        """Generate human-readable insight text based on skill comparison.
        
        Args:
            skill_tag: The skill being analyzed
            child_score: Child's score for this skill (0.0 to 1.0)
            class_average: Class average for this skill
            deviation: Number of standard deviations from mean
            
        Returns:
            Human-readable insight text
        """
        skill_name = SKILL_DISPLAY_NAMES.get(skill_tag, skill_tag)
        
        # Handle missing data cases
        if child_score is None:
            return f"No data available for {skill_name}. More activities needed to assess this skill."
        
        if class_average is None:
            return f"{skill_name} score is {child_score:.0%}. Class comparison not available."
        
        # Generate comparison-based insight
        if deviation is None or abs(deviation) < InsightService.SIGNIFICANT_DEVIATION_THRESHOLD:
            return f"{skill_name} is at {child_score:.0%}, close to the class average of {class_average:.0%}."
        
        if deviation < -InsightService.SIGNIFICANT_DEVIATION_THRESHOLD:
            return (
                f"{skill_name} is at {child_score:.0%}, which is below the class average of {class_average:.0%}. "
                f"Consider targeted activities to support development in this area."
            )
        
        # deviation > SIGNIFICANT_DEVIATION_THRESHOLD
        return (
            f"{skill_name} is at {child_score:.0%}, which is above the class average of {class_average:.0%}. "
            f"This child shows strength in this area."
        )
    
    @staticmethod
    def get_activity_suggestions(skill_tag: str) -> list[str]:
        """Get activity suggestions for a specific skill tag.
        
        Args:
            skill_tag: The skill tag to get suggestions for
            
        Returns:
            List of activity suggestion strings
            
        Raises:
            InvalidSkillTagError: If skill_tag is not valid
        """
        if skill_tag not in VALID_SKILL_TAGS:
            raise InvalidSkillTagError(f"Invalid skill tag: {skill_tag}. Valid tags are: {VALID_SKILL_TAGS}")
        
        suggestions = ActivitySuggestion.query.filter_by(skill_tag=skill_tag).all()
        return [s.activity_text for s in suggestions]
    
    @staticmethod
    def get_child_insights(child_id: int) -> list[Insight]:
        """Get insights for a child based on skill scores relative to class averages.
        
        Args:
            child_id: ID of the child
            
        Returns:
            List of Insight objects for each skill tag
            
        Raises:
            ChildNotFoundError: If child doesn't exist
        """
        child = db.session.get(Child, child_id)
        if child is None:
            raise ChildNotFoundError(f"Child with id {child_id} not found")
        
        # Get child's skill profile
        child_profile = AnalyticsService.get_skill_profile(child_id)
        
        # Get class skill overview for comparison
        class_overview = AnalyticsService.get_class_skill_overview(child.class_id)
        
        # Compute standard deviations for each skill in the class
        # We need to get all children's scores to compute std dev
        class_children = Child.query.filter_by(class_id=child.class_id).all()
        skill_scores_by_tag = {tag: [] for tag in VALID_SKILL_TAGS}
        
        for class_child in class_children:
            profile = AnalyticsService.get_skill_profile(class_child.id)
            profile_dict = profile.to_dict()
            for tag in VALID_SKILL_TAGS:
                score = profile_dict.get(tag)
                if score is not None:
                    skill_scores_by_tag[tag].append(score)
        
        # Generate insights for each skill
        insights = []
        child_profile_dict = child_profile.to_dict()
        
        for skill_tag in VALID_SKILL_TAGS:
            child_score = child_profile_dict.get(skill_tag)
            class_average = class_overview.class_averages.get(skill_tag)
            
            # Compute deviation from mean
            deviation = None
            scores = skill_scores_by_tag[skill_tag]
            if child_score is not None and class_average is not None and len(scores) >= 2:
                std_dev = InsightService._compute_standard_deviation(scores)
                if std_dev > 0:
                    deviation = (child_score - class_average) / std_dev
            
            # Generate insight text
            insight_text = InsightService._generate_insight_text(
                skill_tag, child_score, class_average, deviation
            )
            
            # Get activity suggestions if child is significantly below average
            suggested_activities = []
            if deviation is not None and deviation < -InsightService.SIGNIFICANT_DEVIATION_THRESHOLD:
                suggested_activities = InsightService.get_activity_suggestions(skill_tag)
            
            insights.append(Insight(
                skill_tag=skill_tag,
                child_score=child_score,
                class_average=class_average,
                deviation=deviation,
                insight_text=insight_text,
                suggested_activities=suggested_activities
            ))
        
        return insights
    
    @staticmethod
    def generate_insight_text(child: Child, class_avg: SkillProfile) -> str:
        """Generate a summary insight text for a child compared to class average.
        
        This is a convenience method that generates a single summary string.
        
        Args:
            child: Child instance
            class_avg: SkillProfile representing class averages
            
        Returns:
            Summary insight text string
        """
        child_profile = AnalyticsService.get_skill_profile(child.id)
        child_dict = child_profile.to_dict()
        class_dict = class_avg.to_dict()
        
        strengths = []
        areas_for_growth = []
        
        for skill_tag in VALID_SKILL_TAGS:
            child_score = child_dict.get(skill_tag)
            class_score = class_dict.get(skill_tag)
            
            if child_score is None or class_score is None:
                continue
            
            skill_name = SKILL_DISPLAY_NAMES.get(skill_tag, skill_tag)
            diff = child_score - class_score
            
            if diff > 0.1:  # 10% above average
                strengths.append(skill_name)
            elif diff < -0.1:  # 10% below average
                areas_for_growth.append(skill_name)
        
        parts = []
        if strengths:
            parts.append(f"Shows strength in: {', '.join(strengths)}.")
        if areas_for_growth:
            parts.append(f"Areas for growth: {', '.join(areas_for_growth)}.")
        
        if not parts:
            return "Performance is close to class average across all skills."
        
        return " ".join(parts)
