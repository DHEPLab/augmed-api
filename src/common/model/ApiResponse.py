from dataclasses import dataclass

from common.model import ErrorCode


@dataclass
class Error:
    code: str
    message: str

    @classmethod
    def build(cls, error: ErrorCode, msg: str = None):
        return cls(error.value, msg if msg else error.name)


@dataclass
class ApiResponse:
    data: object | None
    error: Error | None

    @classmethod
    def success(cls, data):
        return cls(data, None)

    @classmethod
    def fail(cls, error: ErrorCode, msg: str = None):
        return cls(None, Error.build(error, msg))
