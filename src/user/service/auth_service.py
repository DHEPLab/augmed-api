from datetime import datetime

from flask_jwt_extended import create_access_token
from werkzeug.exceptions import NotFound, Unauthorized
from werkzeug.security import check_password_hash

from src.user.controller.request.loginRequest import LoginRequest
from src.user.controller.response.loginResponse import LoginResponse
from src.user.repository.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, login_request: LoginRequest) -> LoginResponse:
        user = self.user_repository.get_user_by_email(login_request.email)

        if not user:
            raise NotFound("User not found")

        if not check_password_hash(user.password, login_request.password):
            raise Unauthorized("Invalid credentials")

        additional_claims = {"last_login_time": datetime.now().isoformat()}
        access_token = create_access_token(
            identity=user.email, additional_claims=additional_claims, fresh=True
        )

        return LoginResponse(access_token=access_token)
