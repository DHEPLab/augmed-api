from src.user.model.reset_password_token import ResetPasswordToken


class ResetPasswordTokenRepository:
    def __init__(self, session):
        self.session = session

    def create_reset_password_token(self, token: ResetPasswordToken):
        self.session.add(token)
        self.session.flush()
        return token
