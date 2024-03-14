# auth_service_test.py

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from src.user.controller.request.loginRequest import LoginRequest
from src.user.model.user import User
from src.user.repository.user_repository import UserRepository
from src.user.service.authService import AuthService
from user.controller.authController import auth_blueprint


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # this test do not mock flask_jwt_extended
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 3600
    JWTManager(app)
    app.register_blueprint(auth_blueprint)
    return app


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
    mock_repo.get_user_by_email.side_effect = lambda email: user if email == user.email else None
    return mock_repo


def test_login_success(user_repository_mock, app, user):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        login_request = LoginRequest(email=user.email, password='password123')
        login_response = auth_service.login(login_request)

        assert login_response.access_token is not None
        assert login_response.refresh_token is not None


def test_login_failure_with_wrong_email(user_repository_mock, app):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        wrong_email_login_request = LoginRequest(email='wrong@example.com', password='password123')
        with pytest.raises(Exception) as exc_info:
            auth_service.login(wrong_email_login_request)

        assert 'User not found' in str(exc_info.value)
        assert exc_info.typename == 'NotFound'


def test_login_failure_with_wrong_password(user_repository_mock, app, user):
    with app.app_context():
        auth_service = AuthService(user_repository_mock)
        login_request = LoginRequest(email=user.email, password='password1234')
        with pytest.raises(Exception) as exc_info:
            auth_service.login(login_request)

        assert 'Invalid credentials' in str(exc_info.value)
        assert exc_info.typename == 'Unauthorized'
