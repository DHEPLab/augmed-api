import secrets
from datetime import datetime

from flask_jwt_extended import create_access_token

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.common.regexp.password import validate_password
from src.common.service.email_service import send_email
from src.user.controller.request.loginRequest import LoginRequest
from src.user.controller.request.signupRequest import SignupRequest
from src.user.controller.response.loginResponse import LoginResponse
from src.user.model.reset_password_token import ResetPasswordToken
from src.user.repository.reset_password_token_repository import \
    ResetPasswordTokenRepository
from src.user.repository.user_repository import UserRepository
from src.user.utils.pcrypt import generate_salt, hash_sha256, pcrypt, verify


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        reset_password_request_repository: ResetPasswordTokenRepository,
    ):
        self.user_repository = user_repository
        self.reset_password_request_repository = reset_password_request_repository

    def login(self, login_request: LoginRequest) -> LoginResponse:
        user = self.user_repository.get_user_by_email(login_request.email)

        if not user:
            raise BusinessException(BusinessExceptionEnum.UserNotInPilot)
        if not user.active:
            raise BusinessException(BusinessExceptionEnum.UserEmailIsNotSignup)
        if not verify(login_request.password, user.salt, user.password):
            raise BusinessException(BusinessExceptionEnum.UserPasswordIncorrect)

        additional_claims = {"last_login_time": datetime.now().isoformat()}
        access_token = create_access_token(
            identity=user.email, additional_claims=additional_claims, fresh=True
        )

        return LoginResponse(access_token=access_token)

    def signup(self, signup_request: SignupRequest) -> int:
        if not validate_password(signup_request.password):
            raise BusinessException(BusinessExceptionEnum.UserPasswordInvalid)

        user = self.user_repository.query_user_by_email(signup_request.email)

        if not user:
            raise BusinessException(BusinessExceptionEnum.UserNotInPilot)
        if user.active:
            raise BusinessException(BusinessExceptionEnum.UserEmailIsAlreadySignup)

        salt = generate_salt()
        updated_user = user.copy(
            salt=salt, password=pcrypt(signup_request.password, salt), active=True
        )

        return self.user_repository.update_user(updated_user).id

    def reset_password_request(self, email: str):
        user = self.user_repository.get_user_by_email(email)

        if not user:
            raise BusinessException(BusinessExceptionEnum.UserNotInPilot)
        if not user.active:
            raise BusinessException(BusinessExceptionEnum.UserEmailIsNotSignup)

        token_url = secrets.token_urlsafe()

        self.reset_password_request_repository.create_reset_password_token(
            ResetPasswordToken(email=email, token=hash_sha256(token_url))
        )

        data = {"link": f"https://augmed.dhep.org/reset-password/{token_url}"}
        SUBJECT = "Forgot your password?"
        TO = [email]
        return send_email(SUBJECT, TO, "reset_password.html", **data)

    def update_password(self, password, reset_token):
        hashed_token = hash_sha256(reset_token)
        reset_password_token = self.reset_password_request_repository.find_by_token(
            hashed_token
        )

        if reset_password_token is None:
            raise BusinessException(BusinessExceptionEnum.InValidResetToken)
        if reset_password_token.is_expired():
            raise BusinessException(BusinessExceptionEnum.ResetTokenExpired)

        user = self.user_repository.query_user_by_email(reset_password_token.email)
        salt = generate_salt()
        updated_user = user.copy(salt=salt, password=pcrypt(password, salt))
        self.user_repository.update_user(updated_user)

        reset_password_token.active = False
