from user.repository.user_repository import UserRepository
from werkzeug.security import generate_password_hash

class UserService:
    @staticmethod
    def add_user(data):
        hashed_password = generate_password_hash(data['password'] + data['salt'])
        return UserRepository.create_user(
            name=data['name'], email=data['email'], title=data['title'],
            password=hashed_password, salt=data['salt']
        )

    @staticmethod
    def get_user(user_id):
        return UserRepository.get_user_by_id(user_id)