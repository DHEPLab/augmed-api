import pytest
from werkzeug.security import generate_password_hash

from src.user.model.user import User
from src.user.repository.user_repository import UserRepository
from src.user.service.user_service import UserService


@pytest.fixture
def user():
    return User(
        id=1,
        name='Test User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        salt='somesalt'
    )


def test_get_user(mocker, user):
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_user_by_id.return_value = user
    user_service = UserService(mock_repo)

    found = user_service.get_user(1)

    assert found.email == user.email


def test_only_add_user_for_not_existed(mocker, user):
    not_exist_user = User(
        name='Test User',
        email='test2@example.com',
    )
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_user_by_email.side_effect = lambda email: user if email == user.email else None
    mock_repo.create_user.return_value = user
    user_service = UserService(mock_repo)
    users = [user, not_exist_user]

    result = user_service.add_inactive_user(users)

    assert result[user.email] == "failed: already existed"
    assert result[not_exist_user.email] == "added"


def test_not_add_user_when_exception(mocker):
    not_exist_user = User(
        name='Test User',
        email='test2@example.com',
    )
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_user_by_email.return_value = None
    mock_repo.create_user.side_effect = ValueError("value error")
    user_service = UserService(mock_repo)
    users = [not_exist_user]

    result = user_service.add_inactive_user(users)

    assert result[not_exist_user.email] == "failed: save failed"


def test_get_users(mocker):
    user = User(
        name='Test User',
        email='test2@example.com',
    )
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_users.return_value = [user]
    user_service = UserService(mock_repo)

    result = user_service.get_users()

    assert result[0] == user

