import json
from dataclasses import asdict, dataclass


@dataclass
class LoginResponse:
    access_token: str
    refresh_token: str

    def to_json(self):
        return json.dumps(asdict(self))
