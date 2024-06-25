from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)

from .multiple_choice import multiple_choice_type_validate
from .paragraph import paragraph_type_validate
from .single_choice import single_choice_type_validate
from .text import text_type_validate


def validate_factory(item: dict):
    type = item["type"]

    if type == "Text":
        text_type_validate(item)
    elif type == "Paragraph":
        paragraph_type_validate(item)
    elif type == "SingleChoice":
        single_choice_type_validate(item)
    elif type == "MultipleChoice":
        multiple_choice_type_validate(item)
    else:
        raise BusinessException(
            BusinessExceptionEnum.InValidDiagnoseConfig,
            "Type should be Text, Paragraph, MultipleChoice or SingleChoice",
        )
