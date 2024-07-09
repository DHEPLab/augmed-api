from sqlalchemy import true

from src.user.model.reset_password_token import ResetPasswordToken


class ResetPasswordTokenRepository:
    def __init__(self, session):
        self.session = session

    def create_reset_password_token(self, token: ResetPasswordToken):
        self.session.add(token)
        self.session.flush()
        return token

    def find_by_token(self, hashed_token) -> ResetPasswordToken:
        query_token = self.session.query(ResetPasswordToken).filter(
            ResetPasswordToken.token == hashed_token,
            ResetPasswordToken.active == true(),
        )
        return query_token.one_or_none()
