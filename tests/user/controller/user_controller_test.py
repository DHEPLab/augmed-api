import json

from user.model.user import User


def test_get_user(client, mocker):
    # Setup user mock
    user = User(name="test", email="goodbye@suwukong.com")
    mocker.patch('src.user.service.user_service.UserService.get_user', return_value=user)

    mocker.patch('user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.get("/api/users/1")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["email"] == user.email
    assert data["name"] == user.name


def test_can_not_get_user(client, mocker):
    mocker.patch('src.user.service.user_service.UserService.get_user', return_value=None)

    mocker.patch('user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)

    response = client.get("/api/users/1")

    assert response.status_code == 404
    error = response.json["error"]
    assert error["code"] == 404


def test_create_users(client):
    request = {
        "users": [{
            "name": "name",
            "email": "test@example.com",
            "position": "position",
            "employer": "employer",
            "area_of_clinical_ex": "area_of_clinical_ex"
        }]
    }

    response = client.post("/api/users", data=json.dumps(request), content_type='application/json')

    assert response.status_code == 201
    data = response.json["data"]
    assert data["test@example.com"] == "added"


def test_invalid_request_params_when_create_users(client):
    request = {
        "users": [
            {
                "name": "name2",
            },
            {
                "name": "name2",
                "email": "test",
            }
        ]
    }

    response = client.post("/api/users", data=json.dumps(request), content_type='application/json')

    assert response.status_code == 400
    error = response.json["error"]
    assert "ValidationError" in error["message"]
