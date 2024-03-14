from dataclasses import dataclass
from typing import List

from dataclass_wizard import JSONWizard

from src.user.model.user import User


@dataclass
class CreateUserRequest(JSONWizard):
    users: List[User]
