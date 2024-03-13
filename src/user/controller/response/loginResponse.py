from dataclasses import dataclass, asdict
import json


@dataclass
class LoginResponse:
    access_token: str
    refresh_token: str
    def to_json(self):
        return json.dumps(asdict(self))
