from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)


def single_choice_type_validate(data: dict):
    if "title" not in data:
        raise BusinessException(
            BusinessExceptionEnum.InValidDiagnoseConfig,
            "A question title is required in single choice.",
        )
    if (
        "options" not in data
        or not isinstance(data["options"], list)
        or len(data["options"]) < 2
    ):
        raise BusinessException(
            BusinessExceptionEnum.InValidDiagnoseConfig,
            "Choice question must contain at least 2 options.",
        )
