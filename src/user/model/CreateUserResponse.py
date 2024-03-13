from dataclasses import dataclass, field
from typing import List


@dataclass
class CreateUserResponse:
    success_emails: List[str] = field(default_factory=list)
    failed_emails: List[str] = field(default_factory=list)
