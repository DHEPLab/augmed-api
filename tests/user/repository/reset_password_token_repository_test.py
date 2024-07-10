from datetime import datetime, timedelta
import pytest


from src.user.repository.reset_password_token_repository import ResetPasswordTokenRepository
from src.user.model.reset_password_token import ResetPasswordToken


def without_ms(time: datetime):
    return time.replace(microsecond=0)


@pytest.fixture(scope="session")
def token_repository(session):
    return ResetPasswordTokenRepository(session)


def test_create_reset_password_token(token_repository):
    token = ResetPasswordToken(email="user@test.com", token="hash_token")

    token_repository.create_reset_password_token(token)

    assert token.id is not None
    assert without_ms(token.expired_at) == without_ms(token.created_timestamp) + timedelta(days=2)


def test_find_reset_password_token_by_hashed_token(token_repository):
    token = ResetPasswordToken(email="user@test.com", token="hash_token")
    token_repository.create_reset_password_token(token)

    found = token_repository.find_by_token(token.token)

    assert found is not None


def test_can_not_find_reset_password_token_when_token_inactive(token_repository):
    token = ResetPasswordToken(email="user@test.com", token="hash_token", active=False)
    token_repository.create_reset_password_token(token)

    found = token_repository.find_by_token(token.token)

    assert found is None
