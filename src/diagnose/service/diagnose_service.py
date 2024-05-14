from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.diagnose.model.diagnose import Diagnose
from src.diagnose.model.diagosis import DiagnoseFormData
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.utils import auth_utils


class DiagnoseService:
    def __init__(
        self,
        diagnose_repository: DiagnoseRepository,
        configuration_repository: ConfigurationRepository,
    ):
        self.diagnose_repository = diagnose_repository
        self.configuration_repository = configuration_repository

    def add_diagnose_response(self, task_id: int, form_data: DiagnoseFormData):
        user_eamil = auth_utils.get_user_email_from_jwt()

        configuration = self.configuration_repository.get_configuration_by_id(task_id)
        if not configuration or configuration.user_email != user_eamil:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        diagnose = Diagnose(
            task_id=task_id,
            case_id=configuration.case_id,
            user_email=user_eamil,
            display_configuration=configuration.path_config,
            diagnosis=form_data.diagnose,
            other=form_data.other,
        )

        return self.diagnose_repository.add_diagnose(diagnose)
