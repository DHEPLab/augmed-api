import json

import pytest

from src.user.controller.request.signupRequest import SignupRequest
from src.user.controller.response.loginResponse import LoginResponse
from src.user.model.user import User
from src.user.repository.user_repository import UserRepository

from src import db


@pytest.fixture
def mock_auth_service(mocker):
    mocker.patch(
        'src.user.service.auth_service.AuthService.login',
        return_value=LoginResponse(access_token="fake_access_token"))

@pytest.fixture
def test_user():
    return User(name="john", email="john@exmaple.com",)

@pytest.fixture
def pilot_user_request(test_user: User):
    return SignupRequest(
        email= test_user.email,
        password="9eNLBWpws6TCGk8_ibQn"
    )


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


def test_sign_up_request_invalid(client,
                                 test_user: User):
    UserRepository(db.session).create_user(test_user)

    signup = {
        "email": "john@exmaple.com",
        "password": "simplepassword"
    }

    response = client.post("/api/auth/signup", data=json.dumps(signup), content_type='application/json')

    assert response.status_code == 500    
    assert {
        "data": None,
        "error": {
            "code": "1001",
            "message": (
                "Passwords must have at least 8 characters and contain at least a letter, "
                "a number and a symbol. Please try again."
            )
        }
    } == response.json


def test_sign_up_success(client,
                         test_user: User):
    UserRepository(db.session).create_user(test_user)

    signup = {
        "email": "john@exmaple.com",
        "password": "9eNLBWpws6TCGk8_ibQn"
    }

    response = client.post("/api/auth/signup", data=json.dumps(signup), content_type='application/json')

    assert response.status_code == 201    
    assert {
        "data": "Sign up successfully",
        "error": None
    } == response.json


def test_sign_up_failed_when_user_is_not_in_pilot(client, 
                                                  test_user: User):
    user = test_user.copy()
    UserRepository(db.session).create_user(user)

    signup = {
        "email": "not-in-pilot@exmaple.com",
        "password": "9eNLBWpws6TCGk8_ibQn"
    }

    response = client.post("/api/auth/signup", data=json.dumps(signup), content_type='application/json')

    assert response.status_code == 500
    assert {
        "data": None,
        "error": {
            "code": "1002",
            "message": "It seems that you are not invited to Pilot group. Please contact dhep.lab@gmail.com"
        }
    } == response.json


def test_sign_up_failed_when_user_aready_sign_up(client,
                                                 test_user: User):
    user = test_user.copy(active=True)
    UserRepository(db.session).create_user(user)
    signup = {
        "email": "john@exmaple.com",
        "password": "9eNLBWpws6TCGk8_ibQn"
    }

    response = client.post("/api/auth/signup", data=json.dumps(signup), content_type='application/json')

    assert response.status_code == 500
    assert {
        "data": None,
        "error": {
            "code": "1003",
            "message": "Email is already sign up, please login."
        }
    } == response.json
