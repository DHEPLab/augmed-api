

import uuid
import pytest

from src.common.exception.db_transaction import db_transaction
from src.user.model.reset_password_token import ResetPasswordToken
from src.user.repository.reset_password_token_repository import ResetPasswordTokenRepository


@pytest.fixture(scope="session")
def token_repository(session):
    return ResetPasswordTokenRepository(session)


@pytest.fixture
def fake_token():
    return ResetPasswordToken(id=uuid.uuid4(), email="user@test.com", token="hash_token")


def biz_service_without_transaction(token_repository, fake_token):
    token_repository.create_reset_password_token(fake_token)
    raise Exception("Biz exception throw")


@db_transaction()
def biz_service_wit_transaction(token_repository, fake_token):
    token_repository.create_reset_password_token(fake_token)
    raise Exception("Biz exception throw")


def test_without_transaction_should_not_db_rollback(token_repository, fake_token):
    with pytest.raises(Exception):
        biz_service_without_transaction(token_repository, fake_token)

    assert token_repository.find_by_token(fake_token.token) is not None


def test_with_transaction_should_db_rollback(token_repository, fake_token):
    with pytest.raises(Exception):
        biz_service_wit_transaction(token_repository, fake_token)

    assert token_repository.find_by_token(fake_token.token) is None
