from dataclasses import dataclass


@dataclass
class SignupRequest:
    email: str
    password: str
