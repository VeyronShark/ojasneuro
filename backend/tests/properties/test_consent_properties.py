"""Property-based tests for consent management.

**Feature: flask-backend, Properties 16, 17, 18: Consent Management**
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import datetime

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child
from app.models.consent import ParentLink
from app.models.event import EventRaw
from app.services.consent_service import ConsentService, ConsentError
from app.schemas.event import VALID_SKILL_TAGS


# Strategies for generating test data
consent_status_strategy = st.sampled_from(['granted', 'denied'])
consent_scope_strategy = st.sampled_from(['full', 'limited', 'analytics_only'])
parent_id_strategy = st.integers(min_value=1, max_value=10000)

child_code_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-')
).filter(lambda x: x.strip())

display_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L',), whitelist_characters=' ')
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


def create_test_school(db_session):
    """Helper to create a test school."""
    school = School(name='Test School', enrolled_families=10, app_installs=20)
    db_session.add(school)
    db_session.commit()
    return school


def create_test_teacher(db_session, school_id):
    """Helper to create a test teacher."""
    teacher = Teacher(
        school_id=school_id,
        email='teacher@test.com',
        name='Test Teacher',
        role='teacher',
    )
    teacher.set_password('password123')
    db_session.add(teacher)
    db_session.commit()
    return teacher


def create_test_class(db_session, school_id, teacher_id):
    """Helper to create a test class."""
    class_ = Class(
        school_id=school_id,
        name='Test Class',
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


def create_test_event(db_session, child_code):
    """Helper to create a test event."""
    event = EventRaw(
        child_code=child_code,
        puzzle_id='puzzle_001',
        skill_tags=['attention', 'patience'],
        started_at=datetime(2024, 1, 15, 10, 0, 0),
        ended_at=datetime(2024, 1, 15, 10, 5, 0),
        completed=True
    )
    db_session.add(event)
    db_session.commit()
    return event


class TestConsentRoundTrip:
    """
    **Feature: flask-backend, Property 16: Consent round-trip**
    **Validates: Requirements 7.1, 7.2**
    
    For any consent submission with child_id, parent_id, and scope, storing and then
    retrieving the consent status SHALL return the same consent_status and a valid timestamp.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        consent_status=consent_status_strategy,
        scope=consent_scope_strategy,
        parent_id=parent_id_strategy
    )
    def test_consent_round_trip_preserves_status_and_scope(self, app, consent_status, scope, parent_id):
        """
        **Feature: flask-backend, Property 16: Consent round-trip**
        **Validates: Requirements 7.1, 7.2**
        """
        with app.app_context():
            # Clear existing data
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id)
            
            # Submit consent
            parent_link = ConsentService.submit_consent(
                child_id=child.id,
                parent_id=parent_id,
                consent_status=consent_status,
                scope=scope
            )
            
            # Retrieve consent status
            retrieved_status = ConsentService.get_consent_status(child.id)
            
            # Assert round-trip consistency
            assert retrieved_status.consent_status == consent_status
            assert retrieved_status.consent_timestamp is not None
            
            # If granted, scope should be preserved
            if consent_status == 'granted':
                assert retrieved_status.consent_scope == scope
                assert retrieved_status.is_consent_granted is True
            else:
                assert retrieved_status.is_consent_granted is False
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        parent_id=parent_id_strategy,
        scope=consent_scope_strategy
    )
    def test_consent_granted_then_denied_updates_status(self, app, parent_id, scope):
        """
        **Feature: flask-backend, Property 16: Consent round-trip**
        **Validates: Requirements 7.1, 7.2**
        
        Consent can be updated from granted to denied.
        """
        with app.app_context():
            # Clear existing data
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id)
            
            # First grant consent
            ConsentService.submit_consent(
                child_id=child.id,
                parent_id=parent_id,
                consent_status='granted',
                scope=scope
            )
            
            # Verify granted
            status1 = ConsentService.get_consent_status(child.id)
            assert status1.is_consent_granted is True
            
            # Then deny consent
            ConsentService.submit_consent(
                child_id=child.id,
                parent_id=parent_id,
                consent_status='denied',
                scope=scope
            )
            
            # Verify denied
            status2 = ConsentService.get_consent_status(child.id)
            assert status2.consent_status == 'denied'
            assert status2.is_consent_granted is False


class TestConsentEnforcementExcludesNonConsentedChildren:
    """
    **Feature: flask-backend, Property 17: Consent enforcement excludes non-consented children**
    **Validates: Requirements 7.3**
    
    For any child without granted consent, individual dashboard queries SHALL NOT
    include that child's individual data. The child's data SHALL only appear in
    anonymized class-level aggregates.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_consented=st.integers(min_value=0, max_value=5),
        num_non_consented=st.integers(min_value=0, max_value=5)
    )
    def test_filter_children_by_consent_excludes_non_consented(self, app, num_consented, num_non_consented):
        """
        **Feature: flask-backend, Property 17: Consent enforcement excludes non-consented children**
        **Validates: Requirements 7.3**
        """
        # Ensure we have at least one child
        assume(num_consented + num_non_consented > 0)
        
        with app.app_context():
            # Clear existing data
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            consented_children = []
            non_consented_children = []
            
            # Create consented children
            for i in range(num_consented):
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Consented Child {i}'
                )
                ConsentService.submit_consent(
                    child_id=child.id,
                    parent_id=i + 1,
                    consent_status='granted',
                    scope='full'
                )
                consented_children.append(child)
            
            # Create non-consented children (either no consent record or denied)
            for i in range(num_non_consented):
                child = create_test_child(
                    db.session, 
                    class_.id, 
                    display_name=f'Non-Consented Child {i}'
                )
                # Half get denied consent, half get no consent record
                if i % 2 == 0:
                    ConsentService.submit_consent(
                        child_id=child.id,
                        parent_id=i + 100,
                        consent_status='denied',
                        scope='full'
                    )
                non_consented_children.append(child)
            
            # Get all children
            all_children = Child.query.filter_by(class_id=class_.id).all()
            
            # Filter by consent
            filtered_children = ConsentService.filter_children_by_consent(
                all_children, 
                require_consent=True
            )
            
            # Assert only consented children are returned
            assert len(filtered_children) == num_consented
            
            filtered_ids = {c.id for c in filtered_children}
            consented_ids = {c.id for c in consented_children}
            non_consented_ids = {c.id for c in non_consented_children}
            
            # All filtered children should be in consented set
            assert filtered_ids == consented_ids
            
            # No non-consented children should be in filtered set
            assert filtered_ids.isdisjoint(non_consented_ids)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(parent_id=parent_id_strategy)
    def test_is_consent_granted_returns_false_for_pending(self, app, parent_id):
        """
        **Feature: flask-backend, Property 17: Consent enforcement excludes non-consented children**
        **Validates: Requirements 7.3**
        
        Children with no consent record should not be considered as having consent.
        """
        with app.app_context():
            # Clear existing data
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id)
            
            # No consent submitted - should return False
            assert ConsentService.is_consent_granted(child.id) is False
            
            # Get consent status - should be pending
            status = ConsentService.get_consent_status(child.id)
            assert status.consent_status == 'pending'
            assert status.is_consent_granted is False


class TestDataDeletionRemovesChildEvents:
    """
    **Feature: flask-backend, Property 18: Data deletion removes child events**
    **Validates: Requirements 7.4**
    
    For any data deletion request for a child, after processing, querying events
    for that child_code SHALL return empty results OR anonymized records.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(num_events=st.integers(min_value=1, max_value=10))
    def test_delete_child_data_removes_all_events(self, app, num_events):
        """
        **Feature: flask-backend, Property 18: Data deletion removes child events**
        **Validates: Requirements 7.4**
        """
        with app.app_context():
            # Clear existing data
            db.session.query(EventRaw).delete()
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            child = create_test_child(db.session, class_.id)
            
            # Create multiple events for the child
            for i in range(num_events):
                event = EventRaw(
                    child_code=child.child_code,
                    puzzle_id=f'puzzle_{i}',
                    skill_tags=['attention'],
                    started_at=datetime(2024, 1, 15, 10, i, 0),
                    ended_at=datetime(2024, 1, 15, 10, i + 1, 0),
                    completed=True
                )
                db.session.add(event)
            db.session.commit()
            
            # Verify events exist
            events_before = EventRaw.query.filter_by(child_code=child.child_code).all()
            assert len(events_before) == num_events
            
            # Delete child data
            result = ConsentService.delete_child_data(child.id)
            assert result is True
            
            # Verify events are deleted
            events_after = EventRaw.query.filter_by(child_code=child.child_code).all()
            assert len(events_after) == 0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        num_events_child1=st.integers(min_value=1, max_value=5),
        num_events_child2=st.integers(min_value=1, max_value=5)
    )
    def test_delete_child_data_only_removes_target_child_events(self, app, num_events_child1, num_events_child2):
        """
        **Feature: flask-backend, Property 18: Data deletion removes child events**
        **Validates: Requirements 7.4**
        
        Deleting one child's data should not affect other children's events.
        """
        with app.app_context():
            # Clear existing data
            db.session.query(EventRaw).delete()
            db.session.query(ParentLink).delete()
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create test data
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            class_ = create_test_class(db.session, school.id, teacher.id)
            
            child1 = create_test_child(db.session, class_.id, display_name='Child 1')
            child2 = create_test_child(db.session, class_.id, display_name='Child 2')
            
            # Create events for child1
            for i in range(num_events_child1):
                event = EventRaw(
                    child_code=child1.child_code,
                    puzzle_id=f'puzzle_c1_{i}',
                    skill_tags=['attention'],
                    started_at=datetime(2024, 1, 15, 10, i, 0),
                    ended_at=datetime(2024, 1, 15, 10, i + 1, 0),
                    completed=True
                )
                db.session.add(event)
            
            # Create events for child2
            for i in range(num_events_child2):
                event = EventRaw(
                    child_code=child2.child_code,
                    puzzle_id=f'puzzle_c2_{i}',
                    skill_tags=['patience'],
                    started_at=datetime(2024, 1, 15, 11, i, 0),
                    ended_at=datetime(2024, 1, 15, 11, i + 1, 0),
                    completed=True
                )
                db.session.add(event)
            db.session.commit()
            
            # Delete child1's data
            ConsentService.delete_child_data(child1.id)
            
            # Verify child1's events are deleted
            events_child1 = EventRaw.query.filter_by(child_code=child1.child_code).all()
            assert len(events_child1) == 0
            
            # Verify child2's events are NOT deleted
            events_child2 = EventRaw.query.filter_by(child_code=child2.child_code).all()
            assert len(events_child2) == num_events_child2
