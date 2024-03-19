from dataclasses import dataclass


@dataclass
class LoginResponse:
    access_token: str
