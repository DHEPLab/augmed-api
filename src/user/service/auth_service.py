from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash

from src.user.controller.request.loginRequest import LoginRequest
from src.user.controller.response.loginResponse import LoginResponse
from src.user.model.user import User


class AuthService:
    def __init__(self, database):
        self.db = database

    def login(self, login_request: LoginRequest) -> LoginResponse:
        user = self.db.session.query(User).filter_by(email=login_request.email).first()

        if user and check_password_hash(user.password, login_request.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            return LoginResponse(access_token=access_token, refresh_token=refresh_token)

        raise Exception("Invalid credentials")
