import re
import pytest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.diagnose.model.diagnose import Diagnose
from src.diagnose.model.diagosis import DiagnoseFormData
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.diagnose.service.diagnose_service import DiagnoseService
from src.user.model.configuration import Configuration
from src.user.repository.configuration_repository import ConfigurationRepository


@pytest.fixture
def task_id():
    return 1


@pytest.fixture
def diagnose_form_data():
    return DiagnoseFormData(
        diagnose=[{"diagnosis": 'diagnose', "rationale": 'rationale', "confidence": 100}],
        other=""
    )


@pytest.fixture
def user_email():
    return 'user@test.com'


@pytest.fixture
def diagnose(task_id, user_email, diagnose_form_data):
    return Diagnose(task_id=task_id,
                    case_id=1,
                    user_email=user_email,
                    display_configuration=[],
                    diagnosis=diagnose_form_data.diagnose,
                    other=diagnose_form_data.other
                    )


@pytest.fixture()
def mock_diagnose_repo(mocker):
    return mocker.Mock(DiagnoseRepository)


@pytest.fixture()
def mock_configuration_repo(mocker):
    return mocker.Mock(ConfigurationRepository)


@pytest.fixture(autouse=True)
def before_each_tests(mocker, user_email):
    mocker.patch('src.user.utils.auth_utils.get_user_email_from_jwt', return_value=user_email)


def test_add_diagnose_response(
        task_id,
        diagnose_form_data,
        user_email,
        mock_diagnose_repo,
        mock_configuration_repo
):
    mock_configuration_repo.get_configuration_by_id.return_value = Configuration(
        path_config=[],
        user_email=user_email,
        case_id=1
    )
    diagnose_service = DiagnoseService(mock_diagnose_repo, mock_configuration_repo)

    diagnose_service.add_diagnose_response(task_id, diagnose_form_data)

    assert mock_diagnose_repo.add_diagnose.called


def test_add_diagnose_response_user_and_case_not_match(
        task_id,
        diagnose_form_data,
        mock_diagnose_repo,
        mock_configuration_repo
):
    mock_configuration_repo.get_configuration_by_id.return_value = Configuration(
        path_config=[],
        user_email="user-not-match@test.com",
        case_id=1
    )

    diagnose_service = DiagnoseService(mock_diagnose_repo, mock_configuration_repo)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAccessToCaseReview.name)):
        diagnose_service.add_diagnose_response(task_id, diagnose_form_data)

