import pytest
from werkzeug.security import generate_password_hash

from src.user.controller.request.loginRequest import LoginRequest
from src.user.model.user import User
from src.user.repository.user_repository import UserRepository
from src.user.service.auth_service import AuthService


@pytest.fixture
def user():
    return User(
        id=1,
        name='Test User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        salt='somesalt'
    )


@pytest.fixture
def user_repository_mock(mocker, user):
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_user_by_email.return_value = user
    return mock_repo


def test_login_success(user_repository_mock, app, user):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        login_request = LoginRequest(email=user.email, password='password123')
        login_response,access_token= auth_service.login(login_request)

    assert access_token is not None
    assert login_response.message == "Login successful"


def test_login_failure_with_wrong_email(user_repository_mock, app):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        wrong_email_login_request = LoginRequest(email='wrong@example.com', password='password123')
        with pytest.raises(Exception) as exc_info:
            auth_service.login(wrong_email_login_request)

    assert 'User not found' in str(exc_info.value)


def test_login_failure_with_wrong_password(user_repository_mock, app, user):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        login_request = LoginRequest(email=user.email, password='password1234')
        with pytest.raises(Exception) as exc_info:
            auth_service.login(login_request)

    assert 'Invalid credentials' in str(exc_info.value)
