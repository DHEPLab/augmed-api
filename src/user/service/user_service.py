from app import app
from src.user.repository.user_repository import UserRepository


class UserService:
    @staticmethod
    def add_inactive_user(users):
        response = {}
        for user in users:
            found = UserRepository.get_user_by_email(user.email)
            # noinspection PyBroadException
            try:
                if found:
                    response[user.email] = "failed: already existed"
                else:
                    UserRepository.create_user(user)
                    response[user.email] = "added"
            except Exception:
                response[user.email] = "failed: save failed"
                app.logger.exception("failed to create user: " + user.email)
        return response

    @staticmethod
    def get_user(user_id):
        return UserRepository.get_user_by_id(user_id)
