from io import StringIO

from werkzeug.exceptions import InternalServerError

from src.common.exception.BusinessException import BusinessException
from src.user.repository.display_config_repository import \
    DisplayConfigRepository
from src.user.utils.csv_parser import parse_csv_stream_to_configurations


class ConfigurationService:
    def __init__(self, repository: DisplayConfigRepository):
        self.repository = repository

    def process_csv_file(self, file_stream: StringIO) -> list[dict[str, str]]:
        # Step 1: parse csv
        try:
            configurations = parse_csv_stream_to_configurations(file_stream)
        except BusinessException as e:
            raise e

        responses = []
        # Step 2: clean db
        try:
            self.repository.clean_configurations()
        except Exception as e:
            raise InternalServerError from e

        # Step 3: Save each configuration from the parsed data
        for config in configurations:
            user_case_key = f"{config.user_email}-{config.case_id}"
            result = {"user_case_key": user_case_key}
            try:
                self.repository.save_configuration(config)
                result["status"] = "added"
            except Exception:
                result["status"] = "failed"
            responses.append(result)

        return responses
