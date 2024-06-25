from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)


def text_type_validate(data: dict):
    if "title" not in data:
        raise BusinessException(
            BusinessExceptionEnum.InValidDiagnoseConfig,
            "A question title is required in text.",
        )
