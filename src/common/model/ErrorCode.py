from dataclasses import dataclass
from enum import Enum


@dataclass
class ErrorCode(Enum):
    INTERNAL_ERROR = 500
    INVALID_PARAMETER = 400
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    BAD_REQUEST = 400
