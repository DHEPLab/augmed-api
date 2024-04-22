from io import BytesIO
from typing import Dict

from werkzeug.exceptions import InternalServerError

from common.exception.BusinessException import (BusinessException,
                                                BusinessExceptionEnum)
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from user.utils.excel_parser import parse_excel_stream_to_configurations


class ConfigurationService:
    def __init__(self, repository: ConfigurationRepository):
        self.repository = repository

    def process_excel_file(self, file_stream: BytesIO) -> Dict[str, str]:

        try:
            configurations = parse_excel_stream_to_configurations(file_stream)
        except Exception as e:
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect) from e

        response = {}
        try:
            self.repository.clean_configurations()
        except Exception as e:
            raise InternalServerError from e

        # Step 3: Save each configuration from the parsed data
        for config in configurations:
            user_case_key = f"{config.user_email}-{config.case_id}"
            try:
                self.repository.save_configuration(config)
                response[user_case_key] = "added"
            except Exception:
                response[user_case_key] = "failed: save failed"

        return response
