from dataclasses import dataclass

from src.common.exception.BusinessException import BusinessExceptionEnum
from src.common.model import ErrorCode


@dataclass
class Error:
    code: str
    message: str

    @classmethod
    def build(cls, error: ErrorCode, msg: str = None):
        return cls(error.value, msg if msg else error.name)

    @classmethod
    def build(cls, e: BusinessExceptionEnum):
        return cls(e.code, e.message)


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

    @classmethod
    def fail(cls, e: BusinessExceptionEnum):
        return cls(None, Error.build(e))
