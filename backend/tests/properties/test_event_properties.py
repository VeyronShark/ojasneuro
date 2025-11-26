"""Property-based tests for event ingestion.

**Feature: flask-backend, Properties 8, 9, 20: Event Ingestion**
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 9.3**
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
from app.services.event_service import EventService
from app.schemas.event import VALID_SKILL_TAGS


# Strategies for generating test data
child_code_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')
).filter(lambda x: x.strip())

puzzle_id_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')
).filter(lambda x: x.strip())

skill_tags_strategy = st.lists(
    st.sampled_from(VALID_SKILL_TAGS),
    min_size=1,
    max_size=5,
    unique=True
)

# Generate timestamps where ended_at is after started_at
@st.composite
def valid_timestamp_pair(draw):
    """Generate a valid (started_at, ended_at) pair where ended_at > started_at."""
    base_time = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    duration_seconds = draw(st.integers(min_value=1, max_value=3600))
    ended_at = base_time + timedelta(seconds=duration_seconds)
    return base_time, ended_at


@st.composite
def valid_event_data(draw):
    """Generate valid event data."""
    started_at, ended_at = draw(valid_timestamp_pair())
    return {
        'child_code': draw(child_code_strategy),
        'puzzle_id': draw(puzzle_id_strategy),
        'skill_tags': draw(skill_tags_strategy),
        'started_at': started_at,
        'ended_at': ended_at,
        'completed': draw(st.booleans())
    }


@st.composite
def invalid_event_data_missing_field(draw):
    """Generate event data with a missing required field."""
    event = draw(valid_event_data())
    field_to_remove = draw(st.sampled_from([
        'child_code', 'puzzle_id', 'skill_tags', 'started_at', 'ended_at', 'completed'
    ]))
    del event[field_to_remove]
    return event, field_to_remove


@st.composite
def invalid_event_data_bad_skill_tags(draw):
    """Generate event data with invalid skill tags."""
    started_at, ended_at = draw(valid_timestamp_pair())
    invalid_tag = draw(st.text(min_size=1, max_size=20).filter(
        lambda x: x not in VALID_SKILL_TAGS and x.strip()
    ))
    return {
        'child_code': draw(child_code_strategy),
        'puzzle_id': draw(puzzle_id_strategy),
        'skill_tags': [invalid_tag],
        'started_at': started_at,
        'ended_at': ended_at,
        'completed': draw(st.booleans())
    }


@st.composite
def invalid_event_data_bad_timestamps(draw):
    """Generate event data where ended_at is before started_at."""
    base_time = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    duration_seconds = draw(st.integers(min_value=1, max_value=3600))
    started_at = base_time + timedelta(seconds=duration_seconds)
    ended_at = base_time  # ended_at is before started_at
    return {
        'child_code': draw(child_code_strategy),
        'puzzle_id': draw(puzzle_id_strategy),
        'skill_tags': draw(skill_tags_strategy),
        'started_at': started_at,
        'ended_at': ended_at,
        'completed': draw(st.booleans())
    }


email_strategy = st.emails()
password_strategy = st.text(
    min_size=8,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))
).filter(lambda x: x.strip() and len(x.strip()) >= 8)


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


def create_test_teacher(db_session, school_id, email, password, name='Test Teacher', role='teacher'):
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


def get_auth_token(client, email, password):
    """Helper to get authentication token."""
    response = client.post(
        '/auth/login',
        json={'email': email, 'password': password},
        content_type='application/json'
    )
    return response.get_json()['token']


class TestEventValidation:
    """
    **Feature: flask-backend, Property 8: Event validation**
    **Validates: Requirements 3.1, 3.3**
    
    For any event missing required fields (child_id, puzzle_id, skill_tags, started_at,
    ended_at, completed) OR containing invalid data types, the Backend SHALL reject
    the event and return validation errors.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_and_field=invalid_event_data_missing_field())
    def test_missing_required_field_rejected(self, app, event_and_field):
        """
        **Feature: flask-backend, Property 8: Event validation**
        **Validates: Requirements 3.1, 3.3**
        """
        event_data, missing_field = event_and_field
        
        with app.app_context():
            # Validate the event
            errors = EventService.validate_event(event_data)
            
            # Assert validation fails
            assert len(errors) > 0
            # Assert the error mentions the missing field
            assert any(missing_field in error for error in errors)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_data=invalid_event_data_bad_skill_tags())
    def test_invalid_skill_tags_rejected(self, app, event_data):
        """
        **Feature: flask-backend, Property 8: Event validation**
        **Validates: Requirements 3.1, 3.3**
        """
        with app.app_context():
            # Validate the event
            errors = EventService.validate_event(event_data)
            
            # Assert validation fails
            assert len(errors) > 0
            # Assert the error mentions skill_tags
            assert any('skill_tags' in error for error in errors)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_data=invalid_event_data_bad_timestamps())
    def test_invalid_timestamps_rejected(self, app, event_data):
        """
        **Feature: flask-backend, Property 8: Event validation**
        **Validates: Requirements 3.1, 3.3**
        """
        with app.app_context():
            # Validate the event
            errors = EventService.validate_event(event_data)
            
            # Assert validation fails
            assert len(errors) > 0
            # Assert the error mentions timestamps
            assert any('ended_at' in error or 'started_at' in error for error in errors)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_data=valid_event_data())
    def test_valid_event_passes_validation(self, app, event_data):
        """
        **Feature: flask-backend, Property 8: Event validation**
        **Validates: Requirements 3.1**
        """
        with app.app_context():
            # Validate the event
            errors = EventService.validate_event(event_data)
            
            # Assert validation passes
            assert len(errors) == 0


class TestValidEventsPersistedCorrectly:
    """
    **Feature: flask-backend, Property 9: Valid events are persisted correctly**
    **Validates: Requirements 3.2, 3.4**
    
    For any valid event submitted to the ingestion endpoint, the event SHALL be stored
    in the database with all fields preserved, and the child_code SHALL correctly
    associate with the child record.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_data=valid_event_data())
    def test_valid_event_persisted_with_all_fields(self, app, event_data):
        """
        **Feature: flask-backend, Property 9: Valid events are persisted correctly**
        **Validates: Requirements 3.2, 3.4**
        """
        with app.app_context():
            # Clear existing events
            db.session.query(EventRaw).delete()
            db.session.commit()
            
            # Ingest the event
            result = EventService.ingest_events([event_data])
            
            # Assert event was accepted
            assert result.total_accepted == 1
            assert result.total_rejected == 0
            
            # Retrieve the event from database
            stored_event = EventRaw.query.filter_by(child_code=event_data['child_code']).first()
            
            # Assert event exists
            assert stored_event is not None
            
            # Assert all fields are preserved
            assert stored_event.child_code == event_data['child_code']
            assert stored_event.puzzle_id == event_data['puzzle_id']
            assert stored_event.skill_tags == event_data['skill_tags']
            assert stored_event.completed == event_data['completed']
            
            # Compare timestamps (allowing for timezone differences)
            assert stored_event.started_at.replace(tzinfo=None) == event_data['started_at'].replace(tzinfo=None)
            assert stored_event.ended_at.replace(tzinfo=None) == event_data['ended_at'].replace(tzinfo=None)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(events=st.lists(valid_event_data(), min_size=1, max_size=10))
    def test_batch_events_all_persisted(self, app, events):
        """
        **Feature: flask-backend, Property 9: Valid events are persisted correctly**
        **Validates: Requirements 3.2**
        """
        with app.app_context():
            # Clear existing events
            db.session.query(EventRaw).delete()
            db.session.commit()
            
            # Ingest the batch
            result = EventService.ingest_events(events)
            
            # Assert all events were accepted
            assert result.total_received == len(events)
            assert result.total_accepted == len(events)
            assert result.total_rejected == 0
            
            # Assert all events are in database
            stored_count = EventRaw.query.count()
            assert stored_count == len(events)


class TestEventsContainOnlyPseudonymousIdentifiers:
    """
    **Feature: flask-backend, Property 20: Events contain only pseudonymous identifiers**
    **Validates: Requirements 9.3**
    
    For any stored event, the record SHALL contain only child_code (pseudonymous token)
    and SHALL NOT contain child display_name, parent information, or other PII.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(event_data=valid_event_data())
    def test_stored_event_contains_only_child_code(self, app, event_data):
        """
        **Feature: flask-backend, Property 20: Events contain only pseudonymous identifiers**
        **Validates: Requirements 9.3**
        """
        with app.app_context():
            # Clear existing events
            db.session.query(EventRaw).delete()
            db.session.commit()
            
            # Ingest the event
            EventService.ingest_events([event_data])
            
            # Retrieve the event
            stored_event = EventRaw.query.filter_by(child_code=event_data['child_code']).first()
            
            # Assert event exists
            assert stored_event is not None
            
            # Get the event as dict (simulating API response)
            event_dict = stored_event.to_dict()
            
            # Assert only child_code is present, not PII fields
            assert 'child_code' in event_dict
            assert 'display_name' not in event_dict
            assert 'parent' not in event_dict
            assert 'parent_id' not in event_dict
            assert 'parent_name' not in event_dict
            assert 'email' not in event_dict
            assert 'phone' not in event_dict
            assert 'address' not in event_dict
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        event_data=valid_event_data(),
        display_name=st.text(
            min_size=5,
            max_size=50,
            alphabet=st.characters(whitelist_categories=('L',))
        ).filter(lambda x: x.strip() and len(x) >= 5)
    )
    def test_event_does_not_leak_child_display_name(self, app, event_data, display_name):
        """
        **Feature: flask-backend, Property 20: Events contain only pseudonymous identifiers**
        **Validates: Requirements 9.3**
        
        Even when a child with display_name exists, the event should not contain it.
        """
        # Ensure display_name is distinct from event fields to avoid false positives
        assume(display_name != event_data['child_code'])
        assume(display_name != event_data['puzzle_id'])
        assume(display_name not in event_data['skill_tags'])
        
        with app.app_context():
            # Clear existing data
            db.session.query(EventRaw).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create a school, class, and child with the same child_code
            school = School(name='Test School', enrolled_families=10, app_installs=20)
            db.session.add(school)
            db.session.commit()
            
            teacher = Teacher(
                school_id=school.id,
                email='teacher@test.com',
                name='Test Teacher',
                role='teacher'
            )
            teacher.set_password('password123')
            db.session.add(teacher)
            db.session.commit()
            
            class_ = Class(
                school_id=school.id,
                name='Test Class',
                grade_level='K',
                primary_teacher_id=teacher.id
            )
            db.session.add(class_)
            db.session.commit()
            
            # Create child with specific child_code matching the event
            child = Child(
                class_id=class_.id,
                display_name=display_name,
                child_code=event_data['child_code'],
                age=5
            )
            db.session.add(child)
            db.session.commit()
            
            # Ingest the event
            EventService.ingest_events([event_data])
            
            # Retrieve the event
            stored_event = EventRaw.query.filter_by(child_code=event_data['child_code']).first()
            
            # Assert event exists
            assert stored_event is not None
            
            # Get the event as dict
            event_dict = stored_event.to_dict()
            
            # Assert 'display_name' key is NOT in the event data (the key itself should not exist)
            assert 'display_name' not in event_dict
            
            # Assert the display_name value does not appear in the serialized event
            # (checking that PII is not leaked through any field)
            assert display_name not in str(event_dict)
            
            # Assert child_code IS in the event data
            assert event_dict['child_code'] == event_data['child_code']
