from user.model.user import User


def test_get_user(client, mocker):
    user = User(name="test", email="goodbye@suwukong.com")
    mocker.patch('src.user.service.user_service.UserService.get_user', return_value=user)

    response = client.get("/api/users/1")

    assert response.status_code == 200
    data = response.json["data"]
    assert data["email"] == user.email
    assert data["name"] == user.name


def test_can_not_get_user(client, mocker):
    mocker.patch('src.user.service.user_service.UserService.get_user', return_value=None)

    response = client.get("/api/users/1")

    assert response.status_code == 404
    error = response.json["error"]
    assert error["code"] == 404
