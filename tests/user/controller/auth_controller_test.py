import pytest
from flask import json

from src.user.controller.response.loginResponse import LoginResponse


@pytest.fixture
def mock_auth_service(mocker):
    mocker.patch('src.user.service.authService.AuthService.login',
                 return_value=LoginResponse(access_token="fake_access_token", refresh_token="fake_refresh_token"))


def test_login_success(client, mock_auth_service):
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", data=json.dumps(login_data), content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['access_token'] == "fake_access_token"
    assert data['refresh_token'] == "fake_refresh_token"
