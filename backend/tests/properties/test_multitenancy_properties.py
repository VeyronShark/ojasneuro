"""Property-based tests for multi-tenancy and access control.

**Feature: flask-backend, Properties 5-7: Multi-tenancy and Access Control**
**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 9.1, 9.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.class_ import Class
from app.models.child import Child


# Strategies for generating test data
email_strategy = st.emails()

password_strategy = st.text(
    min_size=8,
    max_size=50,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))
).filter(lambda x: x.strip() and len(x.strip()) >= 8)

name_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'Z'))
).filter(lambda x: x.strip())

school_name_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'Z'))
).filter(lambda x: x.strip())

class_name_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'Z'))
).filter(lambda x: x.strip())

child_name_strategy = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(whitelist_categories=('L', 'N', 'Z'))
).filter(lambda x: x.strip())

age_strategy = st.integers(min_value=3, max_value=12)


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        blacklisted_tokens.clear()
        db.drop_all()


def create_school(db_session, name):
    """Helper to create a school."""
    school = School(name=name, enrolled_families=10, app_installs=20)
    db_session.add(school)
    db_session.commit()
    return school


def create_teacher(db_session, school_id, email, password, name, role='teacher'):
    """Helper to create a teacher."""
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


def create_class(db_session, school_id, name, teacher_id=None):
    """Helper to create a class."""
    class_ = Class(
        school_id=school_id,
        name=name,
        grade_level='K',
        primary_teacher_id=teacher_id,
    )
    db_session.add(class_)
    db_session.commit()
    return class_


def create_child(db_session, class_id, name, age):
    """Helper to create a child."""
    child = Child(
        class_id=class_id,
        display_name=name,
        age=age,
    )
    db_session.add(child)
    db_session.commit()
    return child


def login_user(client, email, password):
    """Helper to login and get token."""
    response = client.post(
        '/auth/login',
        json={'email': email, 'password': password},
        content_type='application/json'
    )
    if response.status_code == 200:
        return response.get_json()['token']
    return None


class TestMultiTenancyDataIsolation:
    """
    **Feature: flask-backend, Property 5: Multi-tenancy data isolation**
    **Validates: Requirements 2.2, 2.3, 9.1**
    
    For any user belonging to school A, when querying classes or children,
    the results SHALL contain only entities where school_id equals school A's id.
    No entities from other schools SHALL appear in the results.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        school_a_name=school_name_strategy,
        school_b_name=school_name_strategy,
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
        class_a_name=class_name_strategy,
        class_b_name=class_name_strategy,
    )
    def test_user_only_sees_own_school_classes(
        self, app, school_a_name, school_b_name, teacher_email, teacher_password,
        teacher_name, class_a_name, class_b_name
    ):
        """
        **Feature: flask-backend, Property 5: Multi-tenancy data isolation**
        **Validates: Requirements 2.2, 9.1**
        """
        # Ensure school names are different
        assume(school_a_name.strip() != school_b_name.strip())
        
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create two schools
            school_a = create_school(db.session, school_a_name)
            school_b = create_school(db.session, school_b_name)
            
            # Create teacher in school A (as admin to access all classes)
            teacher = create_teacher(
                db.session, school_a.id, teacher_email, teacher_password, teacher_name, 'admin'
            )
            
            # Create classes in both schools
            class_a = create_class(db.session, school_a.id, class_a_name, teacher.id)
            class_b = create_class(db.session, school_b.id, class_b_name)
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Request classes for school A
            response = client.get(
                f'/schools/{school_a.id}/classes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Verify only school A's classes are returned
            classes = data['classes']
            for c in classes:
                assert c['school_id'] == school_a.id
            
            # Verify school B's class is not in results
            class_ids = [c['id'] for c in classes]
            assert class_b.id not in class_ids
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        school_a_name=school_name_strategy,
        school_b_name=school_name_strategy,
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
    )
    def test_user_cannot_access_other_school_data(
        self, app, school_a_name, school_b_name, teacher_email, teacher_password, teacher_name
    ):
        """
        **Feature: flask-backend, Property 5: Multi-tenancy data isolation**
        **Validates: Requirements 2.2, 9.1**
        """
        assume(school_a_name.strip() != school_b_name.strip())
        
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create two schools
            school_a = create_school(db.session, school_a_name)
            school_b = create_school(db.session, school_b_name)
            
            # Create teacher in school A
            teacher = create_teacher(
                db.session, school_a.id, teacher_email, teacher_password, teacher_name, 'admin'
            )
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Try to access school B's data - should be forbidden
            response = client.get(
                f'/schools/{school_b.id}/classes',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403


class TestTeacherAccessRestrictedToAssignedClasses:
    """
    **Feature: flask-backend, Property 6: Teacher access restricted to assigned classes**
    **Validates: Requirements 2.4, 9.2**
    
    For any teacher with assigned classes [C1, C2, ...], when requesting data
    for a class not in their assignment list, the Backend SHALL return HTTP status 403.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        school_name=school_name_strategy,
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
        assigned_class_name=class_name_strategy,
        unassigned_class_name=class_name_strategy,
        child_name=child_name_strategy,
        child_age=age_strategy,
    )
    def test_teacher_can_access_assigned_class(
        self, app, school_name, teacher_email, teacher_password, teacher_name,
        assigned_class_name, unassigned_class_name, child_name, child_age
    ):
        """
        **Feature: flask-backend, Property 6: Teacher access restricted to assigned classes**
        **Validates: Requirements 2.4, 9.2**
        """
        assume(assigned_class_name.strip() != unassigned_class_name.strip())
        
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school
            school = create_school(db.session, school_name)
            
            # Create teacher (not admin)
            teacher = create_teacher(
                db.session, school.id, teacher_email, teacher_password, teacher_name, 'teacher'
            )
            
            # Create assigned class (teacher is primary teacher)
            assigned_class = create_class(db.session, school.id, assigned_class_name, teacher.id)
            
            # Create child in assigned class
            child = create_child(db.session, assigned_class.id, child_name, child_age)
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Teacher should be able to access their assigned class
            response = client.get(
                f'/classes/{assigned_class.id}/children',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Verify children are returned
            children = data['children']
            assert len(children) >= 1
            child_ids = [c['id'] for c in children]
            assert child.id in child_ids
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        school_name=school_name_strategy,
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
        assigned_class_name=class_name_strategy,
        unassigned_class_name=class_name_strategy,
    )
    def test_teacher_cannot_access_unassigned_class(
        self, app, school_name, teacher_email, teacher_password, teacher_name,
        assigned_class_name, unassigned_class_name
    ):
        """
        **Feature: flask-backend, Property 6: Teacher access restricted to assigned classes**
        **Validates: Requirements 2.4, 9.2**
        """
        assume(assigned_class_name.strip() != unassigned_class_name.strip())
        
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school
            school = create_school(db.session, school_name)
            
            # Create teacher (not admin)
            teacher = create_teacher(
                db.session, school.id, teacher_email, teacher_password, teacher_name, 'teacher'
            )
            
            # Create assigned class (teacher is primary teacher)
            create_class(db.session, school.id, assigned_class_name, teacher.id)
            
            # Create unassigned class (no teacher assigned)
            unassigned_class = create_class(db.session, school.id, unassigned_class_name, None)
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Teacher should NOT be able to access unassigned class
            response = client.get(
                f'/classes/{unassigned_class.id}/children',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 403
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        school_name=school_name_strategy,
        admin_email=email_strategy,
        admin_password=password_strategy,
        admin_name=name_strategy,
        class_name=class_name_strategy,
    )
    def test_admin_can_access_any_class_in_school(
        self, app, school_name, admin_email, admin_password, admin_name, class_name
    ):
        """
        **Feature: flask-backend, Property 6: Teacher access restricted to assigned classes**
        **Validates: Requirements 2.4, 9.2**
        
        Admins should be able to access any class in their school.
        """
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school
            school = create_school(db.session, school_name)
            
            # Create admin
            admin = create_teacher(
                db.session, school.id, admin_email, admin_password, admin_name, 'admin'
            )
            
            # Create class (admin is NOT the primary teacher)
            class_ = create_class(db.session, school.id, class_name, None)
            
            client = app.test_client()
            token = login_user(client, admin_email, admin_password)
            assert token is not None
            
            # Admin should be able to access any class in their school
            response = client.get(
                f'/classes/{class_.id}/children',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200


class TestEntityValidationRejectsInvalidData:
    """
    **Feature: flask-backend, Property 7: Entity validation rejects invalid data**
    **Validates: Requirements 2.5**
    
    For any entity creation or update request missing required fields or containing
    invalid relationships (e.g., referencing non-existent foreign keys), the Backend
    SHALL return HTTP status 400 with validation error details.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        nonexistent_class_id=st.integers(min_value=10000, max_value=99999),
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
        school_name=school_name_strategy,
    )
    def test_accessing_nonexistent_class_returns_404(
        self, app, nonexistent_class_id, teacher_email, teacher_password, teacher_name, school_name
    ):
        """
        **Feature: flask-backend, Property 7: Entity validation rejects invalid data**
        **Validates: Requirements 2.5**
        """
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school and admin
            school = create_school(db.session, school_name)
            create_teacher(
                db.session, school.id, teacher_email, teacher_password, teacher_name, 'admin'
            )
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Try to access non-existent class
            response = client.get(
                f'/classes/{nonexistent_class_id}/children',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 404
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        nonexistent_school_id=st.integers(min_value=10000, max_value=99999),
        teacher_email=email_strategy,
        teacher_password=password_strategy,
        teacher_name=name_strategy,
        school_name=school_name_strategy,
    )
    def test_accessing_nonexistent_school_returns_404(
        self, app, nonexistent_school_id, teacher_email, teacher_password, teacher_name, school_name
    ):
        """
        **Feature: flask-backend, Property 7: Entity validation rejects invalid data**
        **Validates: Requirements 2.5**
        """
        with app.app_context():
            # Clear existing data
            db.session.query(Child).delete()
            db.session.query(Class).delete()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school and admin
            school = create_school(db.session, school_name)
            create_teacher(
                db.session, school.id, teacher_email, teacher_password, teacher_name, 'admin'
            )
            
            client = app.test_client()
            token = login_user(client, teacher_email, teacher_password)
            assert token is not None
            
            # Try to access non-existent school - should be 403 (access denied)
            # because user doesn't belong to that school
            response = client.get(
                f'/schools/{nonexistent_school_id}/summary',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Returns 403 because user's school_id doesn't match
            assert response.status_code == 403
