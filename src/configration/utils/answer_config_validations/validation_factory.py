from enum import Enum

from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)

from .multiple_choice import multiple_choice_type_validate
from .paragraph import paragraph_type_validate
from .single_choice import single_choice_type_validate
from .text import text_type_validate


class FormType(Enum):
    Text = "Text"
    Paragraph = "Paragraph"
    SingleChoice = "SingleChoice"
    MultipleChoice = "MultipleChoice"


def validate_factory(item: dict):
    type = item["type"]

    if type == FormType.Text.value:
        text_type_validate(item)
    elif type == FormType.Paragraph.value:
        paragraph_type_validate(item)
    elif type == FormType.SingleChoice.value:
        single_choice_type_validate(item)
    elif type == FormType.MultipleChoice.value:
        multiple_choice_type_validate(item)
    else:
        form_type_names = [form_type.value for form_type in FormType]
        raise BusinessException(
            BusinessExceptionEnum.InValidAnswerConfig,
            f"Type should be {', '.join(form_type_names[:-1])} or {form_type_names[-1]}",
        )
