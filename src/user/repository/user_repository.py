from src import db
from src.user.model.user import User


class UserRepository:
    @staticmethod
    def create_user(user: User):
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
