from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash

from src.user.controller.request.loginRequest import LoginRequest
from src.user.controller.response.loginResponse import LoginResponse
from src.user.repository.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def login(self, login_request: LoginRequest) -> LoginResponse:
        user = self.user_repository.get_user_by_email(login_request.email)

        if user and check_password_hash(user.password, login_request.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return LoginResponse(access_token=access_token, refresh_token=refresh_token)

        raise Exception("Invalid credentials")
