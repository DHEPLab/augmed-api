# auth_controller_test.py

import pytest
from flask import Flask, json
from werkzeug.security import generate_password_hash

from src.user.controller.authController import auth_blueprint
from src.user.controller.response.loginResponse import LoginResponse
from src.user.model.user import User
from src.user.repository.user_repository import UserRepository
from src.user.service.auth_service import AuthService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(auth_blueprint)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# Mock the AuthService
@pytest.fixture
def mock_auth_service(mocker, user_repository_mock):
    auth_service = AuthService(user_repository=user_repository_mock)
    auth_service.login = mocker.Mock(return_value=LoginResponse(
        access_token="fake_access_token",
        refresh_token="fake_refresh_token"
    ))
    mocker.patch('src.user.controller.authController.auth_service', new=auth_service)
    return auth_service


@pytest.fixture
def user_repository_mock(mocker):
    mock = mocker.Mock(UserRepository)
    mock.get_user_by_email.return_value = User(
        id=1,
        name='Test User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        salt='somesalt',
    )
    return mock


# Test the login route
def test_login(client, mock_auth_service):
    # Given
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }

    # When
    response = client.post("/auth/login", data=json.dumps(login_data), content_type='application/json')

    # Then
    assert response.status_code == 200
    response_data = response.get_json()
    assert 'access_token' in response_data
    assert 'refresh_token' in response_data
    assert response_data['access_token'] == 'fake_access_token'
    assert response_data['refresh_token'] == 'fake_refresh_token'
