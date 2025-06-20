from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)


def paragraph_type_validate(data: dict):
    if "title" not in data:
        raise BusinessException(
            BusinessExceptionEnum.InValidAnswerConfig,
            "A question title is required in paragraph.",
        )
