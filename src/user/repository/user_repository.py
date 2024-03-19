from sqlalchemy import select

from src.user.model.user import User


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create_user(self, user: User):
        self.session.add(user)
        self.session.flush()
        return user

    def get_user_by_id(self, user_id):
        return self.session.get(User, user_id)

    def get_user_by_email(self, email):
        statement = select(User).filter_by(email=email)
        return self.session.execute(statement).scalar_one_or_none()

    def get_users(self):
        return self.session.query(User).all()
