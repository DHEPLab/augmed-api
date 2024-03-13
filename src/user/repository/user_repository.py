from sqlalchemy import select

from user.model.user import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_user(self, user: User):
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def get_user_by_id(self, user_id):
        statement = select(User).filter_by(id=user_id)
        result = self.db.session.execute(statement).scalar_one_or_none()
        return result

    def get_user_by_email(self, email):
        statement = select(User).filter_by(email=email)
        result = self.db.session.execute(statement).scalar_one_or_none()
        return result
