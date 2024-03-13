from dataclasses import dataclass

from common.model.ErrorCode import ErrorCode


@dataclass
class Error:
    code: str
    message: str

    @classmethod
    def build(cls, error: ErrorCode):
        return cls(error.code, error.message)


@dataclass
class ApiResponse:
    data: object | None
    error: Error | None

    @classmethod
    def success(cls, data):
        return cls(data, None)

    @classmethod
    def fail(cls, error: ErrorCode):
        return cls(None, Error.build(error))
