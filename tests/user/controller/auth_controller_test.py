import json

import pytest

from src.user.controller.response.loginResponse import LoginResponse


@pytest.fixture
def mock_auth_service(mocker):
    mocker.patch(
        'src.user.service.auth_service.AuthService.login',
        return_value=LoginResponse(access_token="fake_access_token"))


def test_login_success(client, mock_auth_service):
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", data=json.dumps(login_data), content_type='application/json')
    assert response.status_code == 200
    data = response.json

    assert data['message'] == "Login Successfully"
    auth_header = response.headers["Authorization"]
    assert auth_header == f"Bearer fake_access_token"
