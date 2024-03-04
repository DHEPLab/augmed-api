from src import db
from src.user.model.user import User


class UserRepository:
    @staticmethod
    def create_user(name, email, title, password, salt):
        user = User(name=name, email=email, title=title, password=password, salt=salt)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
