from dataclasses import dataclass, field
from typing import List


@dataclass
class CreateUserResponse:
    r: List[dict] = field(default_factory=list)
