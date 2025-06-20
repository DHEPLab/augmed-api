import unittest
from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
from src.configration.utils.answer_config_validations.multiple_choice import (
    multiple_choice_type_validate,
)


class TestMultipleChoiceTypeValidate(unittest.TestCase):
    def test_valid_data(self):
        data = {"title": "Sample question?", "options": ["Option 1", "Option 2"]}
        try:
            multiple_choice_type_validate(data)
        except BusinessException:
            self.fail(
                "multiple_choice_type_validate() raised BusinessException unexpectedly!"
            )

    def test_missing_title(self):
        data = {"options": ["Option 1", "Option 2"]}
        with self.assertRaises(BusinessException) as cm:
            multiple_choice_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(
            cm.exception.detail, "A question title is required in multiple choice."
        )

    def test_missing_options(self):
        data = {"title": "Sample question?"}
        with self.assertRaises(BusinessException) as cm:
            multiple_choice_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(
            cm.exception.detail, "Choice question must contain at least 2 options."
        )

    def test_options_not_list(self):
        data = {"title": "Sample question?", "options": "Not a list"}
        with self.assertRaises(BusinessException) as cm:
            multiple_choice_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(
            cm.exception.detail, "Choice question must contain at least 2 options."
        )

    def test_options_length_less_than_two(self):
        data = {"title": "Sample question?", "options": ["Only one option"]}
        with self.assertRaises(BusinessException) as cm:
            multiple_choice_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(
            cm.exception.detail, "Choice question must contain at least 2 options."
        )
