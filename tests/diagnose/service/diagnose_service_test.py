from datetime import datetime
import re
import uuid
import pytest
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from src.configration.model.answer_config import AnswerConfig
from src.configration.repository.answer_config_repository import AnswerConfigurationRepository
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.diagnose.service.diagnose_service import DiagnoseService
from src.user.model.configuration import Configuration
from src.user.repository.configuration_repository import ConfigurationRepository


@pytest.fixture
def task_id():
    return 1


@pytest.fixture
def user_email():
    return 'user@test.com'


@pytest.fixture
def dict_data():
    return {
        "answerConfigId": uuid.uuid4(),
        "answer": {"question": "answer", "question2": "answer2"}
    }


@pytest.fixture()
def mock_diagnose_repo(mocker):
    return mocker.Mock(DiagnoseRepository)


@pytest.fixture()
def mock_configuration_repo(mocker):
    return mocker.Mock(ConfigurationRepository)


@pytest.fixture()
def mock_answer_config_repo(mocker):
    return mocker.Mock(AnswerConfigurationRepository)


@pytest.fixture(autouse=True)
def before_each_tests(mocker, user_email):
    mocker.patch('src.user.utils.auth_utils.get_user_email_from_jwt', return_value=user_email)


def test_add_diagnose_response(
        task_id,
        user_email,
        dict_data,
        mock_diagnose_repo,
        mock_configuration_repo,
        mock_answer_config_repo
):
    mock_configuration_repo.get_configuration_by_id.return_value = Configuration(
        path_config=[],
        user_email=user_email,
        case_id=1
    )
    mock_answer_config_repo.get_answer_config.return_value = AnswerConfig(
        id=dict_data["answerConfigId"],
        config=[{"type": "Text", "title": "title"}],
        created_timestamp=datetime.now()
    )
    diagnose_service = DiagnoseService(mock_diagnose_repo, mock_configuration_repo, mock_answer_config_repo)

    diagnose_service.add_diagnose_response(task_id, dict_data)

    assert mock_diagnose_repo.add_diagnose.called


def test_add_diagnose_response_user_and_case_not_match(
        task_id,
        dict_data,
        mock_diagnose_repo,
        mock_configuration_repo,
        mock_answer_config_repo
):
    mock_configuration_repo.get_configuration_by_id.return_value = Configuration(
        path_config=[],
        user_email="user-not-match@test.com",
        case_id=1
    )

    diagnose_service = DiagnoseService(mock_diagnose_repo, mock_configuration_repo, mock_answer_config_repo)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAccessToCaseReview.name)):
        diagnose_service.add_diagnose_response(task_id, dict_data)


def test_add_diagnose_response_failed_with_no_answer_config(
        task_id,
        user_email,
        dict_data,
        mock_diagnose_repo,
        mock_configuration_repo,
        mock_answer_config_repo
):
    mock_configuration_repo.get_configuration_by_id.return_value = Configuration(
        path_config=[],
        user_email=user_email,
        case_id=1
    )
    mock_answer_config_repo.get_answer_config.return_value = None

    diagnose_service = DiagnoseService(mock_diagnose_repo, mock_configuration_repo, mock_answer_config_repo)

    with pytest.raises(BusinessException, match=re.compile(BusinessExceptionEnum.NoAnswerConfigAvailable.name)):
        diagnose_service.add_diagnose_response(task_id, dict_data)
