import uuid
import pytest

from src.configration.model.answer_config import AnswerConfig
from src.configration.repository.answer_config_repository import AnswerConfigurationRepository


@pytest.fixture
def answer_config_repository(session):
    return AnswerConfigurationRepository(session)


def test_add_answer_config(answer_config_repository):
    config = AnswerConfig(config={"type": "MultipleChoice", "title": "title", "options": ["A", "B"]})

    answer_config_repository.add_answer_config(config)

    assert config.id is not None


def test_query_latest_answer_config(answer_config_repository):
    config1 = AnswerConfig(config={"type": "Text", "title": "first add"})
    config2 = AnswerConfig(config={"type": "Paragraph", "title": "second add"})
    config3 = AnswerConfig(config={"type": "SingleChoice", "title": "title", "options": ["A", "B"]})

    answer_config_repository.add_answer_config(config1)
    answer_config_repository.add_answer_config(config2)
    answer_config_repository.add_answer_config(config3)

    ret = answer_config_repository.query_latest_answer_config()

    assert ret.config["type"] == "SingleChoice"


def test_query_latest_answer_config_with_empty(answer_config_repository):
    assert answer_config_repository.query_latest_answer_config() is None


def test_get_answer_config(answer_config_repository):
    not_exist_answer_config_id = uuid.uuid4()
    assert answer_config_repository.get_answer_config(not_exist_answer_config_id) is None

    config = AnswerConfig(config={"type": "MultipleChoice", "title": "title", "options": ["A", "B"]})
    answer_config_repository.add_answer_config(config)
    assert answer_config_repository.get_answer_config(config.id) is not None
