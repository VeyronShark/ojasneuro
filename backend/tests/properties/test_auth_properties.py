"""Property-based tests for authentication.

**Feature: flask-backend, Properties 1-4: Authentication**
**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
import json

from app import create_app, db, blacklisted_tokens
from app.models.school import School
from app.models.teacher import Teacher


# Strategies for generating test data
email_strategy = st.emails()

# Password strategy - valid passwords (non-empty, reasonable length)
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

role_strategy = st.sampled_from(['teacher', 'admin'])


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        # Clear blacklisted tokens between tests
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


def create_test_teacher(db_session, school_id, email, password, name, role):
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


class TestAuthenticationReturnsValidTokenAndProfile:
    """
    **Feature: flask-backend, Property 1: Authentication returns valid token and profile**
    **Validates: Requirements 1.1, 1.4**
    
    For any valid user credentials (email/password combination that exists in the database),
    calling the login endpoint SHALL return a valid JWT token and a user profile containing
    the user's id, name, email, and role.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        email=email_strategy,
        password=password_strategy,
        name=name_strategy,
        role=role_strategy,
    )
    def test_valid_credentials_return_token_and_profile(self, app, email, password, name, role):
        """
        **Feature: flask-backend, Property 1: Authentication returns valid token and profile**
        **Validates: Requirements 1.1, 1.4**
        """
        with app.app_context():
            # Clear any existing data
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school and teacher
            school = create_test_school(db.session)
            teacher = create_test_teacher(db.session, school.id, email, password, name, role)
            
            # Attempt login
            client = app.test_client()
            response = client.post(
                '/auth/login',
                json={'email': email, 'password': password},
                content_type='application/json'
            )
            
            # Assert successful login
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Assert token is returned
            assert 'token' in data
            assert isinstance(data['token'], str)
            assert len(data['token']) > 0
            
            # Assert user profile is returned with required fields
            assert 'user' in data
            user = data['user']
            assert user['id'] == teacher.id
            assert user['name'] == name
            assert user['email'] == email
            assert user['role'] == role


class TestInvalidCredentialsReturn401:
    """
    **Feature: flask-backend, Property 2: Invalid credentials return 401**
    **Validates: Requirements 1.2**
    
    For any credential combination where the email does not exist OR the password
    does not match, calling the login endpoint SHALL return HTTP status 401.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        valid_email=email_strategy,
        valid_password=password_strategy,
        wrong_password=password_strategy,
        name=name_strategy,
        role=role_strategy,
    )
    def test_wrong_password_returns_401(self, app, valid_email, valid_password, wrong_password, name, role):
        """
        **Feature: flask-backend, Property 2: Invalid credentials return 401**
        **Validates: Requirements 1.2**
        """
        # Ensure passwords are different
        assume(valid_password != wrong_password)
        
        with app.app_context():
            # Clear any existing data
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Create school and teacher
            school = create_test_school(db.session)
            create_test_teacher(db.session, school.id, valid_email, valid_password, name, role)
            
            # Attempt login with wrong password
            client = app.test_client()
            response = client.post(
                '/auth/login',
                json={'email': valid_email, 'password': wrong_password},
                content_type='application/json'
            )
            
            # Assert 401 returned
            assert response.status_code == 401
            
            data = response.get_json()
            assert 'error' in data
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        nonexistent_email=email_strategy,
        password=password_strategy,
    )
    def test_nonexistent_email_returns_401(self, app, nonexistent_email, password):
        """
        **Feature: flask-backend, Property 2: Invalid credentials return 401**
        **Validates: Requirements 1.2**
        """
        with app.app_context():
            # Clear any existing data
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            blacklisted_tokens.clear()
            db.session.commit()
            
            # Attempt login with non-existent email (no users in database)
            client = app.test_client()
            response = client.post(
                '/auth/login',
                json={'email': nonexistent_email, 'password': password},
                content_type='application/json'
            )
            
            # Assert 401 returned
            assert response.status_code == 401
            
            data = response.get_json()
            assert 'error' in data


class TestLogoutInvalidatesSession:
    """
    **Feature: flask-backend, Property 3: Logout invalidates session**
    **Validates: Requirements 1.3**
    
    For any valid authenticated session, after calling logout, subsequent requests
    using the same token SHALL return HTTP status 401.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        email=email_strategy,
        password=password_strategy,
        name=name_strategy,
        role=role_strategy,
    )
    def test_logout_invalidates_token(self, app, email, password, name, role):
        """
        **Feature: flask-backend, Property 3: Logout invalidates session**
        **Validates: Requirements 1.3**
        """
        with app.app_context():
            # Clear any existing data - must clear blacklist first to avoid stale tokens
            blacklisted_tokens.clear()
            db.session.query(Teacher).delete()
            db.session.query(School).delete()
            db.session.commit()
            
            # Create school and teacher
            school = create_test_school(db.session)
            create_test_teacher(db.session, school.id, email, password, name, role)
            
            client = app.test_client()
            
            # Login to get token
            login_response = client.post(
                '/auth/login',
                json={'email': email, 'password': password},
                content_type='application/json'
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.get_json()}"
            token = login_response.get_json()['token']
            
            # Verify token works before logout
            me_response = client.get(
                '/auth/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert me_response.status_code == 200, f"Token should work before logout: {me_response.get_json()}"
            
            # Logout
            logout_response = client.post(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert logout_response.status_code == 200, f"Logout failed: {logout_response.get_json()}"
            
            # Verify token no longer works after logout
            me_response_after = client.get(
                '/auth/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert me_response_after.status_code == 401, f"Token should be invalid after logout: {me_response_after.get_json()}"


class TestProtectedEndpointsRequireAuthentication:
    """
    **Feature: flask-backend, Property 4: Protected endpoints require authentication**
    **Validates: Requirements 1.5**
    
    For any protected endpoint and any request without a valid authentication token,
    the Backend SHALL return HTTP status 401.
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    @given(
        invalid_token=st.text(
            min_size=10,
            max_size=100,
            alphabet=st.characters(whitelist_categories=('L', 'N'), blacklist_characters='\n\r\t ')
        ).filter(lambda x: x.strip() and ' ' not in x),
    )
    def test_invalid_token_returns_401(self, app, invalid_token):
        """
        **Feature: flask-backend, Property 4: Protected endpoints require authentication**
        **Validates: Requirements 1.5**
        
        Note: We filter tokens to exclude whitespace and special characters that would
        cause HTTP header parsing issues, as those are transport-layer concerns rather
        than authentication logic.
        """
        with app.app_context():
            client = app.test_client()
            
            # Try to access protected endpoint with invalid token
            response = client.get(
                '/auth/me',
                headers={'Authorization': f'Bearer {invalid_token}'}
            )
            
            # Assert 401 or 422 returned (422 for malformed JWT)
            assert response.status_code in [401, 422]
    
    def test_no_token_returns_401(self, app):
        """
        **Feature: flask-backend, Property 4: Protected endpoints require authentication**
        **Validates: Requirements 1.5**
        """
        with app.app_context():
            client = app.test_client()
            
            # Try to access protected endpoint without token
            response = client.get('/auth/me')
            
            # Assert 401 returned
            assert response.status_code == 401
    
    def test_logout_without_token_returns_401(self, app):
        """
        **Feature: flask-backend, Property 4: Protected endpoints require authentication**
        **Validates: Requirements 1.5**
        """
        with app.app_context():
            client = app.test_client()
            
            # Try to logout without token
            response = client.post('/auth/logout')
            
            # Assert 401 returned
            assert response.status_code == 401
