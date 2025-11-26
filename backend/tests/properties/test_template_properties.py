"""Property-based tests for template retrieval.

**Feature: flask-backend, Property 19: Template retrieval returns content**
**Validates: Requirements 8.1, 8.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher
from app.models.template import MessageTemplate
from app.services.template_service import (
    TemplateService,
    TemplateNotFoundError,
    InvalidTemplateTypeError,
    VALID_TEMPLATE_TYPES,
    DEFAULT_LANGUAGE,
)


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


def create_test_teacher(db_session, school_id, email='teacher@test.com', password='password123'):
    """Helper to create a test teacher with credentials."""
    teacher = Teacher(
        school_id=school_id,
        email=email,
        name='Test Teacher',
        role='teacher',
    )
    teacher.set_password(password)
    db_session.add(teacher)
    db_session.commit()
    return teacher


def create_message_template(db_session, template_type, language, content):
    """Helper to create a message template."""
    template = MessageTemplate(
        template_type=template_type,
        language=language,
        content=content
    )
    db_session.add(template)
    db_session.commit()
    return template


def clear_test_data(db_session):
    """Helper to clear all test data."""
    db_session.query(MessageTemplate).delete()
    db_session.query(Teacher).delete()
    db_session.query(School).delete()
    db_session.commit()


class TestTemplateRetrievalReturnsContent:
    """
    **Feature: flask-backend, Property 19: Template retrieval returns content**
    **Validates: Requirements 8.1, 8.2**
    
    For any valid template type and language combination that exists in the database,
    the template endpoint SHALL return non-empty content string.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        template_type=st.sampled_from(VALID_TEMPLATE_TYPES),
        language=st.sampled_from(['en', 'es', 'fr', 'de']),
        content=st.text(min_size=10, max_size=500).filter(lambda x: x.strip())
    )
    def test_template_retrieval_returns_stored_content(self, app, template_type, language, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1, 8.2**
        
        For any valid template type and language, retrieving a stored template
        should return the exact content that was stored.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create template with generated data
            create_message_template(db.session, template_type, language, content)
            
            # Retrieve template
            retrieved_content = TemplateService.get_template(template_type, language)
            
            # Assert content matches
            assert retrieved_content == content
            assert len(retrieved_content) > 0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        language=st.sampled_from(['en', 'es', 'fr']),
        content=st.text(min_size=10, max_size=500).filter(lambda x: x.strip())
    )
    def test_parent_message_retrieval_returns_content(self, app, language, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1**
        
        For any language with a parent_message template, get_parent_message
        should return non-empty content.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create parent message template
            create_message_template(db.session, 'parent_message', language, content)
            
            # Retrieve template
            retrieved_content = TemplateService.get_parent_message(language)
            
            # Assert content matches and is non-empty
            assert retrieved_content == content
            assert len(retrieved_content) > 0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        language=st.sampled_from(['en', 'es', 'fr']),
        content=st.text(min_size=10, max_size=500).filter(lambda x: x.strip())
    )
    def test_handout_retrieval_returns_content(self, app, language, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.2**
        
        For any language with a handout template, get_handout
        should return non-empty content.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create handout template
            create_message_template(db.session, 'handout', language, content)
            
            # Retrieve template as text
            retrieved_content = TemplateService.get_handout(format='text', language=language)
            
            # Assert content matches and is non-empty
            assert retrieved_content == content
            assert len(retrieved_content) > 0
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        content=st.text(min_size=10, max_size=200).filter(lambda x: x.strip())
    )
    def test_language_fallback_to_default(self, app, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.3**
        
        When a template doesn't exist for the requested language,
        the service should fall back to the default language (en).
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create template only in default language
            create_message_template(db.session, 'parent_message', DEFAULT_LANGUAGE, content)
            
            # Request in a different language
            retrieved_content = TemplateService.get_parent_message('fr')
            
            # Should fall back to default language content
            assert retrieved_content == content
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        template_type=st.sampled_from(VALID_TEMPLATE_TYPES),
        language=st.sampled_from(['en', 'es', 'fr'])
    )
    def test_template_not_found_raises_error(self, app, template_type, language):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1, 8.2**
        
        When no template exists for the type/language (and no fallback),
        a TemplateNotFoundError should be raised.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Don't create any templates
            
            # Attempt to retrieve should raise error
            with pytest.raises(TemplateNotFoundError):
                TemplateService.get_template(template_type, language)
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        invalid_type=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x not in VALID_TEMPLATE_TYPES
        )
    )
    def test_invalid_template_type_raises_error(self, app, invalid_type):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1, 8.2**
        
        Invalid template types should raise an InvalidTemplateTypeError.
        """
        with app.app_context():
            with pytest.raises(InvalidTemplateTypeError):
                TemplateService.get_template(invalid_type, 'en')


class TestTemplateRoutesReturnContent:
    """
    **Feature: flask-backend, Property 19: Template retrieval returns content**
    **Validates: Requirements 8.1, 8.2**
    
    API routes should return template content for authenticated users.
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        content=st.text(min_size=10, max_size=200).filter(lambda x: x.strip())
    )
    def test_parent_message_route_returns_content(self, app, client, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1**
        
        GET /templates/parent-message should return template content for authenticated users.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create template
            create_message_template(db.session, 'parent_message', 'en', content)
            
            # Login to get token
            login_response = client.post('/auth/login', json={
                'email': 'teacher@test.com',
                'password': 'password123'
            })
            token = login_response.get_json()['token']
            
            # Request template
            response = client.get(
                '/templates/parent-message',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['content'] == content
            assert data['template_type'] == 'parent_message'
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        content=st.text(min_size=10, max_size=200).filter(lambda x: x.strip())
    )
    def test_handout_route_returns_content(self, app, client, content):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.2**
        
        GET /templates/handout should return template content for authenticated users.
        """
        with app.app_context():
            clear_test_data(db.session)
            
            # Create test infrastructure
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id)
            
            # Create template
            create_message_template(db.session, 'handout', 'en', content)
            
            # Login to get token
            login_response = client.post('/auth/login', json={
                'email': 'teacher@test.com',
                'password': 'password123'
            })
            token = login_response.get_json()['token']
            
            # Request template
            response = client.get(
                '/templates/handout',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['content'] == content
            assert data['template_type'] == 'handout'
    
    def test_template_routes_require_authentication(self, app, client):
        """
        **Feature: flask-backend, Property 19: Template retrieval returns content**
        **Validates: Requirements 8.1, 8.2**
        
        Template routes should require authentication.
        """
        with app.app_context():
            # Request without token
            response = client.get('/templates/parent-message')
            assert response.status_code == 401
            
            response = client.get('/templates/handout')
            assert response.status_code == 401
