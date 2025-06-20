import re
from datetime import datetime, timedelta

import pytest
from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
from src.user.controller.request.signupRequest import SignupRequest

from src.user.controller.request.loginRequest import LoginRequest
from src.user.model.reset_password_token import ResetPasswordToken
from src.user.model.user import User
from src.user.repository.reset_password_token_repository import (
    ResetPasswordTokenRepository,
)
from src.user.repository.user_repository import UserRepository
from src.user.service.auth_service import AuthService
from src.user.utils.pcrypt import pcrypt


@pytest.fixture
def user():
    return User(
        id=1,
        name="Test User",
        email="test@example.com",
        password=pcrypt("password123", salt="somesalt"),
        salt="somesalt",
        active=True,
    )


@pytest.fixture
def user_repository_mock(mocker, user):
    mock_repo = mocker.Mock(UserRepository)
    mock_repo.get_user_by_email.return_value = user
    mock_repo.query_user_by_email.return_value = None
    return mock_repo


@pytest.fixture
def reset_password_token_repo_mock(mocker):
    return mocker.Mock(ResetPasswordTokenRepository)


@pytest.fixture
def invalid_singup_request():
    return SignupRequest("john@example.com", "simple password")


@pytest.fixture
def valid_singup_request():
    return SignupRequest("john@example.com", "9eNLBWpws6TCGk8_ibQn")


def test_login_success(user_repository_mock, app, user, reset_password_token_repo_mock):
    with app.app_context():
        auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
        login_request = LoginRequest(email=user.email, password="password123")
        login_response = auth_service.login(login_request)
    assert login_response.access_token is not None


def test_login_failure_with_not_invited_email(
    user_repository_mock, app, reset_password_token_repo_mock
):
    with app.app_context():
        auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
        user_repository_mock.get_user_by_email.return_value = None
        wrong_email_login_request = LoginRequest(
            email="wrong@example.com", password="password123"
        )
        with pytest.raises(
            BusinessException,
            match=re.compile(BusinessExceptionEnum.UserNotInPilot.name),
        ):
            auth_service.login(wrong_email_login_request)


def test_login_failure_with_not_sign_up_email(
    user_repository_mock, app, user, reset_password_token_repo_mock
):
    with app.app_context():
        auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
        user_repository_mock.get_user_by_email.return_value = user.copy(active=False)
        email_not_sign_up_login_request = LoginRequest(
            email=user.email, password="password123"
        )
        with pytest.raises(
            BusinessException,
            match=re.compile(BusinessExceptionEnum.UserEmailIsNotSignup.name),
        ):
            auth_service.login(email_not_sign_up_login_request)


def test_login_failure_with_wrong_password(
    user_repository_mock, app, user, reset_password_token_repo_mock
):
    with app.app_context():
        auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
        login_request = LoginRequest(email=user.email, password="password1234")
        with pytest.raises(
            BusinessException,
            match=re.compile(BusinessExceptionEnum.UserPasswordIncorrect.name),
        ):
            auth_service.login(login_request)


def test_signup_should_failed_when_user_password_is_invalid(
    user_repository_mock, invalid_singup_request, reset_password_token_repo_mock
):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)

    with pytest.raises(
        BusinessException,
        match=re.compile(BusinessExceptionEnum.UserPasswordInvalid.name),
    ):
        auth_service.signup(invalid_singup_request)


def test_signup_should_failed_when_user_not_in_pilot(
    user_repository_mock, valid_singup_request, reset_password_token_repo_mock
):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)

    with pytest.raises(
        BusinessException, match=re.compile(BusinessExceptionEnum.UserNotInPilot.name)
    ):
        auth_service.signup(valid_singup_request)


def test_signup_should_failed_when_user_already_signup(
    user, user_repository_mock, valid_singup_request, reset_password_token_repo_mock
):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
    user_repository_mock.query_user_by_email.return_value = user.copy(active=True)

    with pytest.raises(
        BusinessException,
        match=re.compile(BusinessExceptionEnum.UserEmailIsAlreadySignup.name),
    ):
        auth_service.signup(valid_singup_request)


def test_reset_password_request_success(
    mocker, user, user_repository_mock, reset_password_token_repo_mock
):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)

    user_repository_mock.get_user_by_email.return_value = user
    reset_password_token_repo_mock.create_reset_password_token.return_value = (
        ResetPasswordToken(email=user.email, token="test_token")
    )

    mocker.patch(
        "src.user.service.auth_service.send_email", return_value="sended_email_id"
    )

    assert auth_service.reset_password_request(user.email) == "sended_email_id"


def test_reset_password_request_should_failed_when_no_user(user, user_repository_mock):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
    user_repository_mock.get_user_by_email.return_value = None

    with pytest.raises(
        BusinessException, match=re.compile(BusinessExceptionEnum.UserNotInPilot.name)
    ):
        auth_service.reset_password_request(user.email)


def test_reset_password_request_should_failed_when_user_not_signup(
    user, user_repository_mock
):
    auth_service = AuthService(user_repository_mock, reset_password_token_repo_mock)
    user_repository_mock.get_user_by_email.return_value = user.copy(
        password=None, salt=None, active=False
    )

    with pytest.raises(
        BusinessException,
        match=re.compile(BusinessExceptionEnum.UserEmailIsNotSignup.name),
    ):
        auth_service.reset_password_request(user.email)


def test_update_password_successfully(mocker, user):
    # given
    reset_password_token_repository = mocker.Mock(ResetPasswordTokenRepository)
    reset_password_token = ResetPasswordToken(
        email="test@test.com",
        token="token",
        expired_at=datetime.utcnow() + timedelta(days=2),
    )
    reset_password_token_repository.find_by_token.return_value = reset_password_token

    user_repository = mocker.Mock(UserRepository)
    user_repository.query_user_by_email.return_value = user

    mocker.patch("src.user.utils.pcrypt.generate_salt", return_value="generated_salt")
    mocker.patch("src.user.utils.pcrypt.pcrypt", return_value="encoded_password")

    # when
    auth_service = AuthService(user_repository, reset_password_token_repository)
    auth_service.update_password("password", "token")

    # Then
    user_repository.update_user.assert_called_with(
        user.copy(salt="generated_salt", password="encoded_password")
    )
    assert reset_password_token.active is False


def test_throw_exception_when_reset_token_is_not_valid(
    mocker, user, user_repository_mock
):
    # given
    reset_password_token_repository = mocker.Mock(ResetPasswordTokenRepository)
    reset_password_token_repository.find_by_token.return_value = None

    # when
    auth_service = AuthService(user_repository_mock, reset_password_token_repository)

    # Then
    with pytest.raises(
        BusinessException,
        match=re.compile(BusinessExceptionEnum.InValidResetToken.name),
    ):
        auth_service.update_password("password", "token")


def test_throw_exception_when_reset_token_is_expired(
    mocker, user, user_repository_mock
):
    # given
    reset_password_token_repository = mocker.Mock(ResetPasswordTokenRepository)
    reset_password_token = ResetPasswordToken(
        email="test@test.com",
        token="token",
        expired_at=datetime.utcnow() + timedelta(days=-1),
    )
    reset_password_token_repository.find_by_token.return_value = reset_password_token

    # when
    auth_service = AuthService(user_repository_mock, reset_password_token_repository)

    # Then
    with pytest.raises(
        BusinessException,
        match=re.compile(BusinessExceptionEnum.ResetTokenExpired.name),
    ):
        auth_service.update_password("password", "token")
