"""Property-based tests for insights and activity suggestions.

**Feature: flask-backend, Properties 12, 13: Insights and Activity Suggestions**
**Validates: Requirements 5.1, 5.2, 5.3**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.event import EventRaw
from app.models.template import ActivitySuggestion
from app.services.insight_service import InsightService, SKILL_DISPLAY_NAMES
from app.schemas.event import VALID_SKILL_TAGS


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        blacklisted_tokens.clear()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


def create_test_school(db_session):
    """Helper to create a test school."""
    school = School(name='Test School', enrolled_families=10, app_installs=20)
    db_session.add(school)
    db_session.commit()
    return school


def create_test_teacher(db_session, school_id, email='teacher@test.com', password='password123', name='Test Teacher', role='teacher'):
    """Helper to create a test teacher with credentials."""
    teacher = Teacher(
        school_id=school_id,
        email=email,
        name=name,
        role=role,
    )
    teacher.set_password(password)
    db_session.add(teacher)
    db_session.commit()
    return teacher


def create_test_class(db_session, school_id, teacher_id, name='Test Class'):
    """Helper to create a test class."""
    class_ = Class(
        school_id=school_id,
        name=name,
        grade_level='K',
        primary_teacher_id=teacher_id
    )
    db_session.add(class_)
    db_session.commit()
    return class_


def create_test_child(db_session, class_id, display_name='Test Child', child_code=None):
    """Helper to create a test child."""
    child = Child(
        class_id=class_id,
        display_name=display_name,
        child_code=child_code,
        age=5
    )
    db_session.add(child)
    db_session.commit()
    return child


def create_test_event(db_session, event_data):
    """Helper to create a test event."""
    event = EventRaw(
        child_code=event_data['child_code'],
        puzzle_id=event_data['puzzle_id'],
        skill_tags=event_data['skill_tags'],
        started_at=event_data['started_at'],
        ended_at=event_data['ended_at'],
        completed=event_data['completed']
    )
    db_session.add(event)
    db_session.commit()
    return event


def create_activity_suggestion(db_session, skill_tag, activity_text):
    """Helper to create an activity suggestion."""
    suggestion = ActivitySuggestion(
        skill_tag=skill_tag,
        activity_text=activity_text
    )
    db_session.add(suggestion)
    db_session.commit()
    return suggestion


def clear_test_data(db_session):
    """Helper to clear all test data."""
    db_session.query(ActivitySuggestion).delete()
    db_session.query(EventRaw).delete()
    db_session.query(Child).delete()
    db_session.query(Class).delete()
    db_session.query(Teacher).delete()
    db_session.query(School).delete()
    db_session.commit()


class TestInsightsReflectSkillComparison:
    """
    **Feature: flask-backend, Property 12: Insights reflect skill comparison**
    **Validates: Requirements 5.1, 5.2**
    
    For any child, the generated insights SHALL reference skills where the child's
    score differs significantly (>1 standard deviation) from the class mean, and
    SHALL include appropriate suggestion text.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        child_score=st.floats(min_value=0.0, max_value=0.3),
        class_avg_score=st.floats(min_value=0.7, max_value=1.0)
    )
    def test_insights_include_suggestions_when_below_average(self, app, child_score, class_avg_score):
        """
        **Feature: flask-backend, Property 12: Insights reflect skill comparison**
        **Validates: Requirements 5.1, 5.2**
        
        When a child's skill score is significantly below class mean,
        insights should include suggested activities.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create activity suggestions for attention skill
            create_activity_suggestion(db.session, 'attention', 'Practice focused breathing exercises')
            create_activity_suggestion(db.session, 'attention', 'Play memory matching games')
            
            # Create the target child with low score
            target_child = create_test_child(
                db.session, class_.id, 
                display_name='Target Child',
                child_code='target_child_001'
            )
            
            # Create events for target child (low completion rate = low score)
            total_events = 10
            completed_events = int(child_score * total_events)
            for i in range(total_events):
                event_data = {
                    'child_code': target_child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': i < completed_events
                }
                create_test_event(db.session, event_data)
            
            # Create other children with high scores to establish class average
            for j in range(3):
                other_child = create_test_child(
                    db.session, class_.id,
                    display_name=f'Other Child {j}',
                    child_code=f'other_child_{j}'
                )
                completed_for_other = int(class_avg_score * total_events)
                for i in range(total_events):
                    event_data = {
                        'child_code': other_child.child_code,
                        'puzzle_id': f'puzzle_{i}',
                        'skill_tags': ['attention'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                        'completed': i < completed_for_other
                    }
                    create_test_event(db.session, event_data)
            
            # Get insights for target child
            insights = InsightService.get_child_insights(target_child.id)
            
            # Find the attention insight
            attention_insight = next((i for i in insights if i.skill_tag == 'attention'), None)
            
            assert attention_insight is not None
            # When significantly below average, suggestions should be included
            if attention_insight.deviation is not None and attention_insight.deviation < -1.0:
                assert len(attention_insight.suggested_activities) > 0


    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(skill_tag=st.sampled_from(VALID_SKILL_TAGS))
    def test_insights_contain_all_skill_tags(self, app, skill_tag):
        """
        **Feature: flask-backend, Property 12: Insights reflect skill comparison**
        **Validates: Requirements 5.1**
        
        Insights should contain an entry for each valid skill tag.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create a child with events
            child = create_test_child(
                db.session, class_.id,
                display_name='Test Child',
                child_code='test_child_001'
            )
            
            # Create an event with the given skill tag
            event_data = {
                'child_code': child.child_code,
                'puzzle_id': 'puzzle_1',
                'skill_tags': [skill_tag],
                'started_at': datetime(2024, 6, 15, 10, 0, 0),
                'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                'completed': True
            }
            create_test_event(db.session, event_data)
            
            # Get insights
            insights = InsightService.get_child_insights(child.id)
            
            # Assert all skill tags are present
            insight_tags = [i.skill_tag for i in insights]
            for tag in VALID_SKILL_TAGS:
                assert tag in insight_tags
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        child_score=st.floats(min_value=0.7, max_value=1.0),
        class_avg_score=st.floats(min_value=0.2, max_value=0.4)
    )
    def test_insights_recognize_strengths(self, app, child_score, class_avg_score):
        """
        **Feature: flask-backend, Property 12: Insights reflect skill comparison**
        **Validates: Requirements 5.1**
        
        When a child's skill score is significantly above class mean,
        insights should recognize this as a strength.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create the target child with high score
            target_child = create_test_child(
                db.session, class_.id,
                display_name='Target Child',
                child_code='target_child_001'
            )
            
            # Create events for target child (high completion rate = high score)
            total_events = 10
            completed_events = int(child_score * total_events)
            for i in range(total_events):
                event_data = {
                    'child_code': target_child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['patience'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': i < completed_events
                }
                create_test_event(db.session, event_data)
            
            # Create other children with low scores
            for j in range(3):
                other_child = create_test_child(
                    db.session, class_.id,
                    display_name=f'Other Child {j}',
                    child_code=f'other_child_{j}'
                )
                completed_for_other = int(class_avg_score * total_events)
                for i in range(total_events):
                    event_data = {
                        'child_code': other_child.child_code,
                        'puzzle_id': f'puzzle_{i}',
                        'skill_tags': ['patience'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                        'completed': i < completed_for_other
                    }
                    create_test_event(db.session, event_data)
            
            # Get insights for target child
            insights = InsightService.get_child_insights(target_child.id)
            
            # Find the patience insight
            patience_insight = next((i for i in insights if i.skill_tag == 'patience'), None)
            
            assert patience_insight is not None
            # When significantly above average, insight text should mention strength
            if patience_insight.deviation is not None and patience_insight.deviation > 1.0:
                assert 'strength' in patience_insight.insight_text.lower()
                # Should NOT include suggestions when above average
                assert len(patience_insight.suggested_activities) == 0


class TestActivitySuggestionsRetrieval:
    """
    **Feature: flask-backend, Property 13: Activity suggestions retrieval**
    **Validates: Requirements 5.3**
    
    For any valid skill tag (attention, patience, sensory, emotionAwareness, bodyAwareness),
    requesting suggestions SHALL return a non-empty list of activity strings from the database.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(skill_tag=st.sampled_from(VALID_SKILL_TAGS))
    def test_activity_suggestions_returns_list_for_valid_skill(self, app, skill_tag):
        """
        **Feature: flask-backend, Property 13: Activity suggestions retrieval**
        **Validates: Requirements 5.3**
        
        For any valid skill tag, get_activity_suggestions should return a list.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create some suggestions for the skill tag
            create_activity_suggestion(db.session, skill_tag, f'Activity 1 for {skill_tag}')
            create_activity_suggestion(db.session, skill_tag, f'Activity 2 for {skill_tag}')
            
            # Get suggestions
            suggestions = InsightService.get_activity_suggestions(skill_tag)
            
            # Assert we get a list with the suggestions we created
            assert isinstance(suggestions, list)
            assert len(suggestions) == 2
            assert all(isinstance(s, str) for s in suggestions)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        skill_tag=st.sampled_from(VALID_SKILL_TAGS),
        num_suggestions=st.integers(min_value=1, max_value=5)
    )
    def test_activity_suggestions_returns_all_suggestions(self, app, skill_tag, num_suggestions):
        """
        **Feature: flask-backend, Property 13: Activity suggestions retrieval**
        **Validates: Requirements 5.3**
        
        All suggestions for a skill tag should be returned.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create suggestions
            for i in range(num_suggestions):
                create_activity_suggestion(db.session, skill_tag, f'Activity {i} for {skill_tag}')
            
            # Get suggestions
            suggestions = InsightService.get_activity_suggestions(skill_tag)
            
            # Assert count matches
            assert len(suggestions) == num_suggestions
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        invalid_tag=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x not in VALID_SKILL_TAGS
        )
    )
    def test_activity_suggestions_rejects_invalid_skill_tag(self, app, invalid_tag):
        """
        **Feature: flask-backend, Property 13: Activity suggestions retrieval**
        **Validates: Requirements 5.3**
        
        Invalid skill tags should raise an error.
        """
        from app.services.insight_service import InvalidSkillTagError
        
        with app.app_context():
            with pytest.raises(InvalidSkillTagError):
                InsightService.get_activity_suggestions(invalid_tag)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(skill_tag=st.sampled_from(VALID_SKILL_TAGS))
    def test_activity_suggestions_returns_empty_when_none_exist(self, app, skill_tag):
        """
        **Feature: flask-backend, Property 13: Activity suggestions retrieval**
        **Validates: Requirements 5.3**
        
        When no suggestions exist for a skill tag, an empty list should be returned.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Don't create any suggestions
            
            # Get suggestions
            suggestions = InsightService.get_activity_suggestions(skill_tag)
            
            # Assert empty list
            assert isinstance(suggestions, list)
            assert len(suggestions) == 0
