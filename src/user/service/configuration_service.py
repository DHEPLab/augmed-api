from io import BytesIO

from werkzeug.exceptions import InternalServerError

from common.exception.BusinessException import (BusinessException,
                                                BusinessExceptionEnum)
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from user.utils.excel_parser import parse_excel_stream_to_configurations


class ConfigurationService:
    def __init__(self, repository: ConfigurationRepository):
        self.repository = repository

    def process_excel_file(self, file_stream: BytesIO) -> list[dict[str, str]]:

        try:
            configurations = parse_excel_stream_to_configurations(file_stream)
        except Exception as e:
            raise BusinessException(BusinessExceptionEnum.ConfigFileIncorrect) from e

        responses = []
        try:
            self.repository.clean_configurations()
        except Exception as e:
            raise InternalServerError from e

        # Step 3: Save each configuration from the parsed data
        for config in configurations:
            user_case_key = f"{config.user_email}-{config.case_id}"
            result = {"user_case_key": user_case_key}  # 创建一个新的字典来存储结果
            try:
                self.repository.save_configuration(config)
                result["status"] = "added"  # 设置状态为 "added"
            except Exception:
                result["status"] = "failed"  # 设置状态为 "failed"
            responses.append(result)  # 添加结果到响应列表中

        return responses
