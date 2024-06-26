import unittest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.utils.answer_config_validations.paragraph import paragraph_type_validate


class TestParagraphTypeValidate(unittest.TestCase):

    def test_valid_data(self):
        data = {
            "title": "Sample question?"
        }
        try:
            paragraph_type_validate(data)
        except BusinessException:
            self.fail("paragraph_type_validate() raised BusinessException unexpectedly!")

    def test_missing_title(self):
        data = {}
        with self.assertRaises(BusinessException) as cm:
            paragraph_type_validate(data)

        self.assertEqual(cm.exception.error, BusinessExceptionEnum.InValidAnswerConfig)
        self.assertEqual(cm.exception.detail, "A question title is required in paragraph.")
