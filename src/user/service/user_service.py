from src.user.repository.user_repository import UserRepository
from user.model.CreateUserResponse import CreateUserResponse


class UserService:
    @staticmethod
    def add_inactive_user(users):
        response = CreateUserResponse()
        for user in users:
            # TODO check many fields, regex for email
            if user.name is None:
                response.failed_emails.append(user.email)
            else:
                UserRepository.create_user(user)
                response.success_emails.append(user.email)
        return response

    @staticmethod
    def get_user(user_id):
        return UserRepository.get_user_by_id(user_id)
