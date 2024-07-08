from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.configration.model.answer_config import AnswerConfig
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.configration.utils.answer_config_validations.validation_factory import \
    validate_factory


class AnswerConfigurationService:
    def __init__(self, repository: AnswerConfigurationRepository):
        self.repository = repository

    def add_new_answer_config(self, config: list[dict]):
        if len(config) == 0:
            raise BusinessException(
                BusinessExceptionEnum.InValidAnswerConfig,
                "Answer config can not be empty list.",
            )

        for item in config:
            validate_factory(item)

        answer_config = AnswerConfig(config=config)

        return self.repository.add_answer_config(answer_config).id

    def get_latest_answer_config(self) -> AnswerConfig:
        answer_config = self.repository.query_latest_answer_config()

        if answer_config is None:
            raise BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)

        return answer_config
