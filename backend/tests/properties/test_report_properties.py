"""Property-based tests for report generation.

**Feature: flask-backend, Properties 14, 15: Report Generation**
**Validates: Requirements 6.1, 6.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime, timedelta, date
from io import BytesIO

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.event import EventRaw
from app.services.report_service import ReportService, ChildReportData, SchoolReportData
from app.services.analytics_service import DateRange
from app.schemas.event import VALID_SKILL_TAGS


# Strategies for generating test data
display_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L',), whitelist_characters=' ')
).filter(lambda x: x.strip())

school_name_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' ')
).filter(lambda x: x.strip())

class_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' -')
).filter(lambda x: x.strip())


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


def create_test_school(db_session, name='Test School'):
    """Helper to create a test school."""
    school = School(name=name, enrolled_families=10, app_installs=20)
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


def create_test_child(db_session, class_id, display_name='Test Child', child_code=None, age=5):
    """Helper to create a test child."""
    child = Child(
        class_id=class_id,
        display_name=display_name,
        child_code=child_code,
        age=age
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


class TestChildReportContainsRequiredData:
    """
    **Feature: flask-backend, Property 14: Child report contains required data**
    **Validates: Requirements 6.1**
    
    For any child with metrics, the generated PDF report SHALL contain the child's
    name, skill profile scores, and recent activity summary.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        child_name=display_name_strategy,
        child_age=st.integers(min_value=3, max_value=12),
        num_events=st.integers(min_value=1, max_value=5)
    )
    def test_child_report_data_contains_child_name(self, app, child_name, child_age, num_events):
        """
        **Feature: flask-backend, Property 14: Child report contains required data**
        **Validates: Requirements 6.1**
        
        The child report data should contain the child's name.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(
                db.session, 
                class_.id, 
                display_name=child_name,
                child_code='test_child_001',
                age=child_age
            )
            
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
            
            # Get report data
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            report_data = ReportService._gather_child_report_data(child.id, date_range)
            
            # Assert child name is in report data
            assert report_data.child_name == child_name
            assert report_data.child_age == child_age
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_events=st.integers(min_value=1, max_value=10),
        skill_tag=st.sampled_from(VALID_SKILL_TAGS)
    )
    def test_child_report_data_contains_skill_scores(self, app, num_events, skill_tag):
        """
        **Feature: flask-backend, Property 14: Child report contains required data**
        **Validates: Requirements 6.1**
        
        The child report data should contain skill profile scores.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(
                db.session, 
                class_.id, 
                display_name='Test Child',
                child_code='test_child_002'
            )
            
            # Create events with the given skill tag
            for i in range(num_events):
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': [skill_tag],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=i),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=i),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get report data
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            report_data = ReportService._gather_child_report_data(child.id, date_range)
            
            # Assert skill scores are present
            assert skill_tag in report_data.skill_scores
            assert report_data.skill_scores[skill_tag] is not None
            # All events completed, so score should be 100.0 (percentage)
            assert report_data.skill_scores[skill_tag] == 100.0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_events=st.integers(min_value=1, max_value=10))
    def test_child_report_data_contains_activity_summary(self, app, num_events):
        """
        **Feature: flask-backend, Property 14: Child report contains required data**
        **Validates: Requirements 6.1**
        
        The child report data should contain recent activity summary (total sessions).
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(
                db.session, 
                class_.id, 
                display_name='Test Child',
                child_code='test_child_003'
            )
            
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
            
            # Get report data
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            report_data = ReportService._gather_child_report_data(child.id, date_range)
            
            # Assert activity summary is present
            assert report_data.total_sessions == num_events
            assert report_data.avg_duration_seconds > 0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_events=st.integers(min_value=1, max_value=5))
    def test_child_report_generates_valid_pdf(self, app, num_events):
        """
        **Feature: flask-backend, Property 14: Child report contains required data**
        **Validates: Requirements 6.1**
        
        The generated child report should be a valid PDF.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(
                db.session, 
                class_.id, 
                display_name='Test Child',
                child_code='test_child_004'
            )
            
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
            
            # Generate PDF
            date_range = DateRange(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )
            pdf_bytes = ReportService.generate_child_report(child.id, date_range)
            
            # Assert PDF is generated and starts with PDF header
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            assert pdf_bytes[:4] == b'%PDF'


class TestSchoolReportContainsAggregatedData:
    """
    **Feature: flask-backend, Property 15: School report contains aggregated data**
    **Validates: Requirements 6.2**
    
    For any school with classes and children, the monthly report PDF SHALL contain
    school-wide engagement metrics and skill score summaries.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_classes=st.integers(min_value=1, max_value=3),
        children_per_class=st.integers(min_value=1, max_value=3)
    )
    def test_school_report_data_contains_total_classes(self, app, num_classes, children_per_class):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain the correct total number of classes.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create classes with children
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                for j in range(children_per_class):
                    child = create_test_child(
                        db.session, 
                        class_.id, 
                        display_name=f'Child {i}_{j}',
                        child_code=f'child_{i}_{j}'
                    )
                    # Create an event for each child
                    event_data = {
                        'child_code': child.child_code,
                        'puzzle_id': f'puzzle_{i}_{j}',
                        'skill_tags': ['attention'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                        'completed': True
                    }
                    create_test_event(db.session, event_data)
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert total classes
            assert report_data.total_classes == num_classes
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_classes=st.integers(min_value=1, max_value=3),
        children_per_class=st.integers(min_value=1, max_value=3)
    )
    def test_school_report_data_contains_total_children(self, app, num_classes, children_per_class):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain the correct total number of children.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create classes with children
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                for j in range(children_per_class):
                    child = create_test_child(
                        db.session, 
                        class_.id, 
                        display_name=f'Child {i}_{j}',
                        child_code=f'child_{i}_{j}'
                    )
                    # Create an event for each child
                    event_data = {
                        'child_code': child.child_code,
                        'puzzle_id': f'puzzle_{i}_{j}',
                        'skill_tags': ['attention'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                        'completed': True
                    }
                    create_test_event(db.session, event_data)
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert total children
            expected_children = num_classes * children_per_class
            assert report_data.total_children == expected_children
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_classes=st.integers(min_value=1, max_value=3),
        events_per_child=st.integers(min_value=1, max_value=3)
    )
    def test_school_report_data_contains_total_sessions(self, app, num_classes, events_per_child):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain the correct total number of sessions.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            total_events = 0
            # Create classes with children and events
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_{i}'
                )
                # Create events for each child
                for j in range(events_per_child):
                    event_data = {
                        'child_code': child.child_code,
                        'puzzle_id': f'puzzle_{i}_{j}',
                        'skill_tags': ['attention'],
                        'started_at': datetime(2024, 6, 15, 10, 0, 0) + timedelta(hours=j),
                        'ended_at': datetime(2024, 6, 15, 10, 30, 0) + timedelta(hours=j),
                        'completed': True
                    }
                    create_test_event(db.session, event_data)
                    total_events += 1
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert total sessions
            assert report_data.total_sessions == total_events
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_classes=st.integers(min_value=1, max_value=3))
    def test_school_report_data_contains_engagement_summary(self, app, num_classes):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain engagement summary.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create classes with children
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_{i}'
                )
                # Create an event
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert engagement summary is present
            assert 'low' in report_data.engagement_summary
            assert 'medium' in report_data.engagement_summary
            assert 'high' in report_data.engagement_summary
            # Total engagement counts should equal number of classes
            total_engagement = (
                report_data.engagement_summary['low'] +
                report_data.engagement_summary['medium'] +
                report_data.engagement_summary['high']
            )
            assert total_engagement == num_classes
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(skill_tag=st.sampled_from(VALID_SKILL_TAGS))
    def test_school_report_data_contains_skill_summaries(self, app, skill_tag):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain skill score summaries.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(
                db.session, 
                class_.id, 
                display_name='Test Child',
                child_code='test_child_001'
            )
            
            # Create event with the given skill tag
            event_data = {
                'child_code': child.child_code,
                'puzzle_id': 'puzzle_1',
                'skill_tags': [skill_tag],
                'started_at': datetime(2024, 6, 15, 10, 0, 0),
                'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                'completed': True
            }
            create_test_event(db.session, event_data)
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert skill summaries are present
            assert skill_tag in report_data.skill_summaries
            assert report_data.skill_summaries[skill_tag] is not None
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_classes=st.integers(min_value=1, max_value=3))
    def test_school_report_generates_valid_pdf(self, app, num_classes):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The generated school report should be a valid PDF.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create classes with children
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_{i}'
                )
                # Create an event
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Generate PDF
            report_month = date(2024, 6, 1)
            pdf_bytes = ReportService.generate_school_report(school.id, report_month)
            
            # Assert PDF is generated and starts with PDF header
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            assert pdf_bytes[:4] == b'%PDF'
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_classes=st.integers(min_value=1, max_value=3))
    def test_school_report_data_contains_class_summaries(self, app, num_classes):
        """
        **Feature: flask-backend, Property 15: School report contains aggregated data**
        **Validates: Requirements 6.2**
        
        The school report data should contain summaries for each class.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create classes with children
            for i in range(num_classes):
                class_ = create_test_class(
                    db.session, 
                    school.id, 
                    teacher.id, 
                    name=f'Class {i}'
                )
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Child {i}',
                    child_code=f'child_{i}'
                )
                # Create an event
                event_data = {
                    'child_code': child.child_code,
                    'puzzle_id': f'puzzle_{i}',
                    'skill_tags': ['attention'],
                    'started_at': datetime(2024, 6, 15, 10, 0, 0),
                    'ended_at': datetime(2024, 6, 15, 10, 30, 0),
                    'completed': True
                }
                create_test_event(db.session, event_data)
            
            # Get report data
            report_month = date(2024, 6, 1)
            report_data = ReportService._gather_school_report_data(school.id, report_month)
            
            # Assert class summaries are present
            assert len(report_data.class_summaries) == num_classes
            for summary in report_data.class_summaries:
                assert 'class_name' in summary
                assert 'total_children' in summary
                assert 'active_children' in summary
                assert 'total_sessions' in summary
                assert 'engagement_level' in summary
