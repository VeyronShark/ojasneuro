"""Property-based tests for JSON serialization round-trip.

**Feature: flask-backend, Property 21: JSON serialization round-trip**
**Validates: Requirements 10.3**
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, date, timedelta

from app import create_app, db
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.event import EventRaw
from app.models.metrics import ChildDailyMetrics, ClassWeeklyMetrics, SchoolWeeklyMetrics
from app.models.consent import ParentLink
from app.models.template import ActivitySuggestion, MessageTemplate


# Strategies for generating test data
school_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(
    whitelist_categories=('L', 'N', 'P', 'Z'),
    whitelist_characters=' -_'
)).filter(lambda x: x.strip())

email_strategy = st.emails()

skill_tags_strategy = st.lists(
    st.sampled_from(['attention', 'patience', 'sensory', 'emotionAwareness', 'bodyAwareness']),
    min_size=1,
    max_size=5
)

hex_color_strategy = st.from_regex(r'^#[0-9A-Fa-f]{6}$', fullmatch=True)


@pytest.fixture(scope='module')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


class TestSchoolSerialization:
    """Property tests for School model serialization."""
    
    @settings(max_examples=100)
    @given(
        name=school_name_strategy,
        enrolled_families=st.integers(min_value=0, max_value=10000),
        app_installs=st.integers(min_value=0, max_value=10000),
    )
    def test_school_round_trip(self, app, name, enrolled_families, app_installs):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        
        For any School instance, serializing to dict and deserializing back
        should produce an equivalent object with all fields preserved.
        """
        with app.app_context():
            # Create original school
            original = School(
                name=name,
                enrolled_families=enrolled_families,
                app_installs=app_installs,
            )
            
            # Serialize to dict (JSON-compatible)
            serialized = original.to_dict()
            
            # Deserialize back
            restored = School.from_dict(serialized)
            
            # Verify all fields are preserved
            assert restored.name == original.name
            assert restored.enrolled_families == original.enrolled_families
            assert restored.app_installs == original.app_installs


class TestTeacherSerialization:
    """Property tests for Teacher model serialization."""
    
    @settings(max_examples=100)
    @given(
        name=school_name_strategy,
        email=email_strategy,
        role=st.sampled_from(['teacher', 'admin']),
    )
    def test_teacher_round_trip(self, app, name, email, role):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        
        For any Teacher instance, serializing to dict and deserializing back
        should produce an equivalent object with all fields preserved.
        Note: password_hash is intentionally excluded from serialization for security.
        """
        with app.app_context():
            # Create original teacher
            original = Teacher(
                school_id=1,
                email=email,
                name=name,
                role=role,
            )
            original.set_password('test_password')
            
            # Serialize to dict (JSON-compatible)
            serialized = original.to_dict()
            
            # Deserialize back
            restored = Teacher.from_dict(serialized)
            
            # Verify all serialized fields are preserved
            assert restored.school_id == original.school_id
            assert restored.email == original.email
            assert restored.name == original.name
            assert restored.role == original.role


class TestClassSerialization:
    """Property tests for Class model serialization."""
    
    @settings(max_examples=100)
    @given(
        name=school_name_strategy,
        grade_level=st.sampled_from(['Pre-K', 'Kindergarten', 'Grade 1', 'Grade 2', 'Grade 3']),
    )
    def test_class_round_trip(self, app, name, grade_level):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = Class(
                school_id=1,
                name=name,
                grade_level=grade_level,
            )
            
            serialized = original.to_dict()
            restored = Class.from_dict(serialized)
            
            assert restored.school_id == original.school_id
            assert restored.name == original.name
            assert restored.grade_level == original.grade_level


class TestChildSerialization:
    """Property tests for Child model serialization."""
    
    @settings(max_examples=100)
    @given(
        display_name=school_name_strategy,
        age=st.integers(min_value=3, max_value=12),
    )
    def test_child_round_trip(self, app, display_name, age):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = Child(
                class_id=1,
                display_name=display_name,
                age=age,
            )
            
            serialized = original.to_dict()
            restored = Child.from_dict(serialized)
            
            assert restored.class_id == original.class_id
            assert restored.display_name == original.display_name
            assert restored.child_code == original.child_code
            assert restored.age == original.age


class TestEventSerialization:
    """Property tests for EventRaw model serialization."""
    
    @settings(max_examples=100)
    @given(
        child_code=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        puzzle_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
        skill_tags=skill_tags_strategy,
        duration_minutes=st.integers(min_value=1, max_value=60),
        completed=st.booleans(),
    )
    def test_event_round_trip(self, app, child_code, puzzle_id, skill_tags, duration_minutes, completed):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            started_at = datetime(2024, 1, 15, 10, 0, 0)
            ended_at = started_at + timedelta(minutes=duration_minutes)
            
            original = EventRaw(
                child_code=child_code,
                puzzle_id=puzzle_id,
                skill_tags=skill_tags,
                started_at=started_at,
                ended_at=ended_at,
                completed=completed,
            )
            
            serialized = original.to_dict()
            restored = EventRaw.from_dict(serialized)
            
            assert restored.child_code == original.child_code
            assert restored.puzzle_id == original.puzzle_id
            assert restored.skill_tags == original.skill_tags
            assert restored.started_at == original.started_at
            assert restored.ended_at == original.ended_at
            assert restored.completed == original.completed


class TestChildDailyMetricsSerialization:
    """Property tests for ChildDailyMetrics model serialization."""
    
    @settings(max_examples=100)
    @given(
        sessions_count=st.integers(min_value=0, max_value=100),
        avg_duration=st.integers(min_value=0, max_value=3600),
        skill_scores=st.fixed_dictionaries({
            'attention': st.floats(min_value=0, max_value=100, allow_nan=False),
            'patience': st.floats(min_value=0, max_value=100, allow_nan=False),
        }),
    )
    def test_child_daily_metrics_round_trip(self, app, sessions_count, avg_duration, skill_scores):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = ChildDailyMetrics(
                child_id=1,
                date=date(2024, 1, 15),
                sessions_count=sessions_count,
                avg_duration=avg_duration,
                skill_scores=skill_scores,
            )
            
            serialized = original.to_dict()
            restored = ChildDailyMetrics.from_dict(serialized)
            
            assert restored.child_id == original.child_id
            assert restored.date == original.date
            assert restored.sessions_count == original.sessions_count
            assert restored.avg_duration == original.avg_duration
            assert restored.skill_scores == original.skill_scores


class TestClassWeeklyMetricsSerialization:
    """Property tests for ClassWeeklyMetrics model serialization."""
    
    @settings(max_examples=100)
    @given(
        engagement_level=st.sampled_from(['low', 'medium', 'high']),
        avg_skill_scores=st.fixed_dictionaries({
            'attention': st.floats(min_value=0, max_value=100, allow_nan=False),
            'patience': st.floats(min_value=0, max_value=100, allow_nan=False),
        }),
    )
    def test_class_weekly_metrics_round_trip(self, app, engagement_level, avg_skill_scores):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = ClassWeeklyMetrics(
                class_id=1,
                week_start_date=date(2024, 1, 15),
                engagement_level=engagement_level,
                avg_skill_scores=avg_skill_scores,
            )
            
            serialized = original.to_dict()
            restored = ClassWeeklyMetrics.from_dict(serialized)
            
            assert restored.class_id == original.class_id
            assert restored.week_start_date == original.week_start_date
            assert restored.engagement_level == original.engagement_level
            assert restored.avg_skill_scores == original.avg_skill_scores


class TestParentLinkSerialization:
    """Property tests for ParentLink model serialization."""
    
    @settings(max_examples=100)
    @given(
        consent_status=st.sampled_from(['pending', 'granted', 'denied']),
        consent_scope=st.sampled_from(['full', 'limited', 'analytics_only']),
    )
    def test_parent_link_round_trip(self, app, consent_status, consent_scope):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = ParentLink(
                child_id=1,
                parent_id=1,
                consent_status=consent_status,
                consent_timestamp=datetime(2024, 1, 15, 10, 0, 0),
                consent_scope=consent_scope,
            )
            
            serialized = original.to_dict()
            restored = ParentLink.from_dict(serialized)
            
            assert restored.child_id == original.child_id
            assert restored.parent_id == original.parent_id
            assert restored.consent_status == original.consent_status
            assert restored.consent_scope == original.consent_scope


class TestActivitySuggestionSerialization:
    """Property tests for ActivitySuggestion model serialization."""
    
    @settings(max_examples=100)
    @given(
        skill_tag=st.sampled_from(['attention', 'patience', 'sensory', 'emotionAwareness', 'bodyAwareness']),
        activity_text=st.text(min_size=10, max_size=500),
    )
    def test_activity_suggestion_round_trip(self, app, skill_tag, activity_text):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = ActivitySuggestion(
                skill_tag=skill_tag,
                activity_text=activity_text,
            )
            
            serialized = original.to_dict()
            restored = ActivitySuggestion.from_dict(serialized)
            
            assert restored.skill_tag == original.skill_tag
            assert restored.activity_text == original.activity_text


class TestMessageTemplateSerialization:
    """Property tests for MessageTemplate model serialization."""
    
    @settings(max_examples=100)
    @given(
        template_type=st.sampled_from(['parent_message', 'handout', 'welcome']),
        language=st.sampled_from(['en', 'es', 'fr', 'de']),
        content=st.text(min_size=10, max_size=1000),
    )
    def test_message_template_round_trip(self, app, template_type, language, content):
        """
        **Feature: flask-backend, Property 21: JSON serialization round-trip**
        **Validates: Requirements 10.3**
        """
        with app.app_context():
            original = MessageTemplate(
                template_type=template_type,
                language=language,
                content=content,
            )
            
            serialized = original.to_dict()
            restored = MessageTemplate.from_dict(serialized)
            
            assert restored.template_type == original.template_type
            assert restored.language == original.language
            assert restored.content == original.content
