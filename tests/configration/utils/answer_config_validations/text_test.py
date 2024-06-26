import unittest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.utils.answer_config_validations.text import text_type_validate


class TestTextTypeValidate(unittest.TestCase):

    def test_valid_data(self):
        data = {
            "title": "Sample question?"
        }
        try:
            text_type_validate(data)
        except BusinessException:
            self.fail("text_type_validate() raised BusinessException unexpectedly!")

    def test_missing_title(self):
        data = {}
        with self.assertRaises(BusinessException) as cm:
            text_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(cm.exception.detail, "A question title is required in text.")
