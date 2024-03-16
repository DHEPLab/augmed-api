import pytest
from sqlalchemy.exc import IntegrityError

from src.user.repository.user_repository import UserRepository  # Replace with your actual UserRepository import
from user.model.user import User


@pytest.fixture(scope="session")
def user_repository(session):
    return UserRepository(session)


def test_create_user(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")

    user_repository.create_user(user)
    created = user_repository.get_user_by_id(user.id)

    assert created.email == user.email
    assert created.id is not None


def test_create_user_failed_due_to_duplicate_email(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    user.id = None
    with pytest.raises(IntegrityError):
        user_repository.create_user(user)


def test_get_user_by_id_success(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    found = user_repository.get_user_by_id(user.id)

    assert found is not None


def test_get_user_by_id_failed(user_repository: UserRepository):
    found = user_repository.get_user_by_id(99999)
    assert found is None


def test_get_user_by_email_success(user_repository: UserRepository):
    user = User(name="123", email="goodbye@sunwukong.com")
    user_repository.create_user(user)

    found = user_repository.get_user_by_email(user.email)

    assert found is not None


def test_get_user_by_email_failed(user_repository, app):
    found = user_repository.get_user_by_email("nonexistent.email@email.com")

    assert found is None
