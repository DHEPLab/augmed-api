from src.user.repository.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def add_inactive_user(self, users):
        response = {}
        for user in users:
            found = self.user_repository.get_user_by_email(user.email)
            # noinspection PyBroadException
            try:
                if found:
                    response[user.email] = "failed: already existed"
                else:
                    self.user_repository.create_user(user)
                    response[user.email] = "added"
            except Exception:
                response[user.email] = "failed: save failed"
                print("failed to create user: " + user.email)
        return response

    def get_user(self, user_id):
        return self.user_repository.get_user_by_id(user_id)
