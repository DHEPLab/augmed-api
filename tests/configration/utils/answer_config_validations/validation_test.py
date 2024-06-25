import re
import unittest
from unittest.mock import patch

import pytest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.utils.answer_config_validations.validation_factory import validate_factory


class TestValidateFactory(unittest.TestCase):

    def test_text_type_validate(self):
        item = {"type": "Text", "title": "title"}
        with patch('src.configration.utils.answer_config_validations.validation_factory.text_type_validate') as mock_text_type_validate:
            validate_factory(item)
            mock_text_type_validate.assert_called_once_with(item)

    def test_paragraph_type_validate(self):
        item = {"type": "Paragraph", "title": "title"}
        with patch('src.configration.utils.answer_config_validations.validation_factory.paragraph_type_validate') as mock_paragraph_type_validate:
            validate_factory(item)
            mock_paragraph_type_validate.assert_called_once_with(item)

    def test_single_choice_type_validate(self):
        item = {"type": "SingleChoice", "title": "title", "options": ["A", "B", "C"]}
        with patch('src.configration.utils.answer_config_validations.validation_factory.single_choice_type_validate') as mock_single_choice_type_validate:
            validate_factory(item)
            mock_single_choice_type_validate.assert_called_once_with(item)

    def test_multiple_choice_type_validate(self):
        item = {"type": "MultipleChoice", "title": "title", "options": ["A", "B", "C"]}
        with patch('src.configration.utils.answer_config_validations.validation_factory.multiple_choice_type_validate') as mock_multiple_choice_type_validate:
            validate_factory(item)
            mock_multiple_choice_type_validate.assert_called_once_with(item)

    def test_invalid_type(self):
        item = {"type": "InvalidType"}
         
        with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.InValidDiagnoseConfig.name)):
            validate_factory(item)
