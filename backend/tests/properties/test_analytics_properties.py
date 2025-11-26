"""Property-based tests for analytics and metrics computation.

**Feature: flask-backend, Properties 10, 11: Analytics and Metrics**
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta, date

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.event import EventRaw
from app.services.analytics_service import AnalyticsService, DateRange
from app.schemas.event import VALID_SKILL_TAGS


# Strategies for generating test data
child_code_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')
).filter(lambda x: x.strip())

puzzle_id_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')
).filter(lambda x: x.strip())

skill_tags_strategy = st.lists(
    st.sampled_from(VALID_SKILL_TAGS),
    min_size=1,
    max_size=5,
    unique=True
)

display_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L',), whitelist_characters=' ')
).filter(lambda x: x.strip())


@st.composite
def valid_timestamp_pair(draw):
    """Generate a valid (started_at, ended_at) pair where ended_at > started_at."""
    base_time = draw(st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2024, 12, 31)
    ))
    duration_seconds = draw(st.integers(min_value=1, max_value=3600))
    ended_at = base_time + timedelta(seconds=duration_seconds)
    return base_time, ended_at


@st.composite
def valid_event_data(draw, child_code=None):
    """Generate valid event data."""
    started_at, ended_at = draw(valid_timestamp_pair())
    return {
        'child_code': child_code or draw(child_code_strategy),
        'puzzle_id': draw(puzzle_id_strategy),
        'skill_tags': draw(skill_tags_strategy),
        'started_at': started_at,
        'ended_at': ended_at,
        'completed': draw(st.booleans())
    }


@st.composite
def events_for_child(draw, child_code):
    """Generate a list of events for a specific child."""
    num_events = draw(st.integers(min_value=1, max_value=10))
    events = []
    for _ in range(num_events):
        started_at, ended_at = draw(valid_timestamp_pair())
        events.append({
            'child_code': child_code,
            'puzzle_id': draw(puzzle_id_strategy),
            'skill_tags': draw(skill_tags_strategy),
            'started_at': started_at,
            'ended_at': ended_at,
            'completed': draw(st.booleans())
        })
    return events


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


def clear_test_data(db_session):
    """Helper to clear all test data."""
    db_session.query(EventRaw).delete()
    db_session.query(Child).delete()
    db_session.query(Class).delete()
    db_session.query(Teacher).delete()
    db_session.query(School).delete()
    db_session.commit()


class TestClassMetricsAggregation:
    """
    **Feature: flask-backend, Property 10: Class metrics aggregation**
    **Validates: Requirements 4.1, 4.4**
    
    For any class with children who have events in a date range, the class metrics
    SHALL correctly aggregate: total sessions, average engagement, and skill score
    distributions across all children in that class.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_children=st.integers(min_value=1, max_value=5),
        events_per_child=st.integers(min_value=1, max_value=5)
    )
    def test_class_metrics_total_sessions_equals_sum_of_events(self, app, num_children, events_per_child):
        """
        **Feature: flask-backend, Property 10: Class metrics aggregation**
        **Validates: Requirements 4.1, 4.4**
        
        Total sessions in class metrics should equal the sum of all events
        for all children in the class within the date range.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create children and events
            total_events = 0
            for i in range(num_children):
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_code_{i}'
                )
                
                # Create events for this child
                for j in range(events_per_child):
                    event_data = {
                        'child_code': child.child_code,
                        'puzzle_id': f'puzzle_{j}',
                        'skill_tags': ['attention'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=j),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=j),
                        'completed': True
                    }
                    create_test_event(db.session, event_data)
                    total_events += 1
            
            # Get class metrics
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            metrics = AnalyticsService.get_class_metrics(class_.id, date_range)
            
            # Assert total sessions equals total events
            assert metrics.total_sessions == total_events
            assert metrics.total_children == num_children
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_active_children=st.integers(min_value=1, max_value=3),
        num_inactive_children=st.integers(min_value=0, max_value=2)
    )
    def test_class_metrics_active_children_count(self, app, num_active_children, num_inactive_children):
        """
        **Feature: flask-backend, Property 10: Class metrics aggregation**
        **Validates: Requirements 4.1, 4.4**
        
        Active children count should equal the number of children with at least one event.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create active children (with events)
            for i in range(num_active_children):
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Active Child {i}',
                    child_code=f'active_child_{i}'
                )
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': 'puzzle_1',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Create inactive children (no events)
            for i in range(num_inactive_children):
                create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Inactive Child {i}',
                    child_code=f'inactive_child_{i}'
                )
            
            # Get class metrics
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            metrics = AnalyticsService.get_class_metrics(class_.id, date_range)
            
            # Assert counts
            assert metrics.total_children == num_active_children + num_inactive_children
            assert metrics.active_children == num_active_children

    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_children=st.integers(min_value=1, max_value=3),
        total_events=st.integers(min_value=1, max_value=10)
    )
    def test_class_metrics_avg_sessions_per_child(self, app, num_children, total_events):
        """
        **Feature: flask-backend, Property 10: Class metrics aggregation**
        **Validates: Requirements 4.1, 4.4**
        
        Average sessions per child should equal total_sessions / total_children.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            # Create children
            children = []
            for i in range(num_children):
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_code_{i}'
                )
                children.append(child)
            
            # Distribute events among children
            for i in range(total_events):
                child = children[i % num_children]
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get class metrics
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            metrics = AnalyticsService.get_class_metrics(class_.id, date_range)
            
            # Assert average sessions per child
            expected_avg = total_events / num_children
            assert abs(metrics.avg_sessions_per_child - expected_avg) < 0.001


class TestChildMetricsComputation:
    """
    **Feature: flask-backend, Property 11: Child metrics computation**
    **Validates: Requirements 4.2, 4.3, 4.5**
    
    For any child with events, the metrics SHALL correctly compute: sessions_count
    as count of distinct sessions, avg_duration as mean of (ended_at - started_at),
    and skill_scores derived from completed puzzles' skill_tags.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_events=st.integers(min_value=1, max_value=10))
    def test_child_metrics_sessions_count_equals_event_count(self, app, num_events):
        """
        **Feature: flask-backend, Property 11: Child metrics computation**
        **Validates: Requirements 4.2, 4.5**
        
        Sessions count should equal the number of events for the child.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id, child_code='test_child_001')
            
            # Create events
            for i in range(num_events):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get child metrics
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            metrics = AnalyticsService.get_child_metrics(child.id, date_range)
            
            # Assert sessions count
            assert metrics.total_sessions == num_events

    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        durations=st.lists(
            st.integers(min_value=60, max_value=3600),
            min_size=1,
            max_size=10
        )
    )
    def test_child_metrics_avg_duration_computed_correctly(self, app, durations):
        """
        **Feature: flask-backend, Property 11: Child metrics computation**
        **Validates: Requirements 4.2, 4.5**
        
        Average duration should equal the mean of all event durations.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id, child_code='test_child_002')
            
            # Create events with specific durations
            for i, duration in enumerate(durations):
                started_at = datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i)
                ended_at = started_at + timedelta(seconds=duration)
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': started_at,
                    'ended_at': ended_at,
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get child metrics
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            metrics = AnalyticsService.get_child_metrics(child.id, date_range)
            
            # Assert average duration
            expected_avg = sum(durations) / len(durations)
            assert abs(metrics.avg_duration_seconds - expected_avg) < 0.001
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        completed_count=st.integers(min_value=0, max_value=5),
        incomplete_count=st.integers(min_value=0, max_value=5)
    )
    def test_child_skill_scores_based_on_completion_rate(self, app, completed_count, incomplete_count):
        """
        **Feature: flask-backend, Property 11: Child metrics computation**
        **Validates: Requirements 4.3, 4.5**
        
        Skill scores should be computed as the ratio of completed to total events
        for each skill tag.
        """
        # Ensure at least one event
        assume(completed_count + incomplete_count > 0)
        
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id, child_code='test_child_003')
            
            # Create completed events
            for i in range(completed_count):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_completed_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Create incomplete events
            for i in range(incomplete_count):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_incomplete_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 14, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 14, 30, 0) + timedelta(hours=i),
                    'completed': False
                }
                create_test_event(db.session, event_data)
            
            # Get skill profile
            profile = AnalyticsService.get_skill_profile(child.id)
            
            # Assert skill score for attention
            total = completed_count + incomplete_count
            expected_score = completed_count / total
            assert abs(profile.attention - expected_score) < 0.001

    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(skill_tag=st.sampled_from(VALID_SKILL_TAGS))
    def test_skill_profile_contains_all_skill_tags(self, app, skill_tag):
        """
        **Feature: flask-backend, Property 11: Child metrics computation**
        **Validates: Requirements 4.3**
        
        Skill profile should contain scores for all valid skill tags.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id, child_code='test_child_004')
            
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
            
            # Get skill profile
            profile = AnalyticsService.get_skill_profile(child.id)
            profile_dict = profile.to_dict()
            
            # Assert the skill tag has a score
            assert skill_tag in profile_dict
            assert profile_dict[skill_tag] is not None
            assert profile_dict[skill_tag] == 1.0  # 100% completion rate
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        start_offset=st.integers(min_value=0, max_value=30),
        end_offset=st.integers(min_value=31, max_value=60)
    )
    def test_child_metrics_date_range_filtering(self, app, start_offset, end_offset):
        """
        **Feature: flask-backend, Property 11: Child metrics computation**
        **Validates: Requirements 4.2**
        
        Child metrics should only include events within the specified date range.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id, child_code='test_child_005')
            
            # Create events inside the date range
            inside_range_count = 3
            for i in range(inside_range_count):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_inside_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(days=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(days=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Create events outside the date range (before)
            for i in range(2):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_before_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 1, 1, 10, 0, 0) + timedelta(days=i),
                    'ended_at': datetime(2024, 1, 1, 10, 30, 0) + timedelta(days=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Create events outside the date range (after)
            for i in range(2):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_after_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 12, 1, 10, 0, 0) + timedelta(days=i),
                    'ended_at': datetime(2024, 12, 1, 10, 30, 0) + timedelta(days=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get child metrics with specific date range
            date_range = DateRange(
                start_date=date(2024, 6, 1),
                end_date=date(2024, 6, 30)
            )
            metrics = AnalyticsService.get_child_metrics(child.id, date_range)
            
            # Assert only events inside the range are counted
            assert metrics.total_sessions == inside_range_count
