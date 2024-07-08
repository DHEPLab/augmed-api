from datetime import datetime
import uuid
import pytest

from src.configration.model.answer_config import AnswerConfig
from src.configration.repository.answer_config_repository import AnswerConfigurationRepository
from src.configration.service.answer_config_service import AnswerConfigurationService


@pytest.fixture()
def test_config():
    return [
        {"type": "Text", "title": "Please make a diagnose"},
        {"type": "SingleChoice", "title": "title", "options": ["A", "B"]}
    ]


@pytest.fixture()
def mock_answer_config_repo(mocker):
    return mocker.Mock(AnswerConfigurationRepository)


@pytest.fixture()
def fake_answer_config(test_config):
    return AnswerConfig(id=uuid.uuid4(), config=test_config, created_timestamp=datetime.now())


def test_add_new_answer_config_success(mock_answer_config_repo, fake_answer_config, test_config):
    mock_answer_config_repo.add_answer_config.return_value = fake_answer_config

    answer_configuration_service = AnswerConfigurationService(mock_answer_config_repo)

    ret = answer_configuration_service.add_new_answer_config(test_config)

    assert ret == fake_answer_config.id


def test_get_latest_answer_config_success(mock_answer_config_repo, fake_answer_config, test_config):
    mock_answer_config_repo.query_latest_answer_config.return_value = fake_answer_config

    answer_configuration_service = AnswerConfigurationService(mock_answer_config_repo)

    ret = answer_configuration_service.get_latest_answer_config()

    assert ret == fake_answer_config