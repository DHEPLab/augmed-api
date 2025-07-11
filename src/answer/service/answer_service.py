from src.answer.model.answer import Answer
from src.answer.repository.answer_repository import AnswerRepository
from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
from src.configration.repository.answer_config_repository import (
    AnswerConfigurationRepository,
)
from src.user.repository.display_config_repository import DisplayConfigRepository
from src.user.utils import auth_utils


class AnswerService:
    def __init__(
        self,
        answer_repository: AnswerRepository,
        configuration_repository: DisplayConfigRepository,
        answer_config_repository: AnswerConfigurationRepository,
    ):
        self.answer_repository = answer_repository
        self.configuration_repository = configuration_repository
        self.answer_config_repository = answer_config_repository

    def add_answer_response(self, task_id: int, data: dict):
        user_email = auth_utils.get_user_email_from_jwt()

        answer = data["answer"]
        answer_config_id = data["answerConfigId"]

        ai_shown = data.get("aiScoreShown", False)

        configuration = self.configuration_repository.get_configuration_by_id(task_id)

        if not configuration or configuration.user_email != user_email:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        answer_config = self.answer_config_repository.get_answer_config(
            answer_config_id
        )
        if answer_config is None:
            raise BusinessException(BusinessExceptionEnum.NoAnswerConfigAvailable)

        diagnose = Answer(
            task_id=task_id,
            case_id=configuration.case_id,
            user_email=user_email,
            ai_score_shown=ai_shown,
            display_configuration=configuration.path_config,
            answer_config_id=answer_config.id,
            answer=answer,
        )

        return self.answer_repository.add_answer(diagnose)
