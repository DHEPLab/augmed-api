from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.diagnose.model.diagnose import Diagnose
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.utils import auth_utils


class DiagnoseService:
    def __init__(
        self,
        diagnose_repository: DiagnoseRepository,
        configuration_repository: ConfigurationRepository,
        answer_config_repository: AnswerConfigurationRepository,
    ):
        self.diagnose_repository = diagnose_repository
        self.configuration_repository = configuration_repository
        self.answer_config_repository = answer_config_repository

    def add_diagnose_response(self, task_id: int, data: dict):
        user_eamil = auth_utils.get_user_email_from_jwt()

        answer = data["answer"]
        answer_config_id = data["answerConfigId"]

        configuration = self.configuration_repository.get_configuration_by_id(task_id)

        if not configuration or configuration.user_email != user_eamil:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        answer_config = self.answer_config_repository.get_answer_config(
            answer_config_id
        )
        if answer_config is None:
            raise BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)

        diagnose = Diagnose(
            task_id=task_id,
            case_id=configuration.case_id,
            user_email=user_eamil,
            display_configuration=configuration.path_config,
            answer_config_id=answer_config.id,
            answer=answer,
        )

        return self.diagnose_repository.add_diagnose(diagnose)
