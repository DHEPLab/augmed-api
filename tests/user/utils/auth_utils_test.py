from datetime import datetime, timedelta, timezone

import jwt
import pytest
from werkzeug.exceptions import Unauthorized
from werkzeug.security import generate_password_hash

from src.user.model.user import User
from src.user.utils.auth_utils import validate_jwt_and_refresh, get_user_email_from_jwt


@pytest.fixture
def user():
    return User(
        id=1,
        name='Test User',
        email='test@example.com',
        password=generate_password_hash('password123'),
        salt='somesalt'
    )


@pytest.fixture
def generate_dummy_jwt():
    dummy_payload = {"sub": "test@example.com", "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
                     "last_login_time": datetime.now(tz=timezone.utc).isoformat()}
    dummy_secret = "super-secret-key"
    token = jwt.encode(dummy_payload, dummy_secret, algorithm="HS256")
    return f"Bearer {token}"


@pytest.fixture
def jwt_request_context(app, mocker, generate_dummy_jwt):
    with app.app_context():
        mocker.patch('flask_jwt_extended.verify_jwt_in_request', return_value=None)
        mocker.patch('flask_jwt_extended.get_jwt_identity', return_value='test@example.com')
        mocker.patch('flask_jwt_extended.get_jwt', return_value={
            "exp": (datetime.now(tz=timezone.utc) + timedelta(minutes=30)).timestamp(),
            "last_login_time": (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat(),
            "sub": "test@example.com"
        })
        with app.test_request_context(headers={"Authorization": generate_dummy_jwt}):
            yield


def test_validate_jwt_not_expired(mocker, app, jwt_request_context, user):
    new_token = validate_jwt_and_refresh()
    assert new_token is None


def test_validate_jwt_expired_new_token_issued(app, jwt_request_context, mocker, user):
    mocker.patch('src.user.utils.auth_utils.get_jwt', return_value={
        "exp": (datetime.now(tz=timezone.utc) - timedelta(minutes=30)).timestamp(),
        "additional_claims": {
            "last_login_time": (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat(),
        }
    })
    new_token = validate_jwt_and_refresh()
    assert new_token is not None


def test_validate_jwt_expired_last_login_over_3_days(app, jwt_request_context, mocker, user):
    mocker.patch('src.user.utils.auth_utils.get_jwt', return_value={
        "exp": (datetime.now(tz=timezone.utc) - timedelta(days=4)).timestamp(),
        "additional_claims": {
            "last_login_time": (datetime.now(tz=timezone.utc) - timedelta(days=4)).isoformat(),
        }
    })

    with pytest.raises(Unauthorized):
        validate_jwt_and_refresh()


def test_validate_jwt_verification_fails(app, jwt_request_context, mocker):
    mocker.patch('src.user.utils.auth_utils.verify_jwt_in_request', side_effect=Unauthorized("Invalid JWT"))
    with pytest.raises(Unauthorized):
        validate_jwt_and_refresh()


def test_get_user_email_from_jwt(app, jwt_request_context):
    user_email = get_user_email_from_jwt()

    assert user_email == "test@example.com"
