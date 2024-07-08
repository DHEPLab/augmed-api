import pytest

from src.answer.model.answer import Answer
from src.answer.repository.answer_repository import AnswerRepository
from src.user.model.display_config import DisplayConfig
from src.user.repository.display_config_repository import DisplayConfigRepository


@pytest.fixture
def diagnose_repository(session):
    return AnswerRepository(session)


@pytest.fixture
def configuration_repository(session):
    return DisplayConfigRepository(session)


def test_add_diagnose(diagnose_repository, configuration_repository):
    config = DisplayConfig(user_email="user@test.com", case_id=1, path_config={"key": "value"})
    configuration_repository.save_configuration(config)

    diagnose = Answer(
        task_id=config.id,
        case_id=1,
        user_email="user@test.com",
        display_configuration=[],
    )

    assert diagnose.id is None

    diagnose_repository.add_answer(diagnose)

    assert diagnose.id is not None


def test_get_diagnosed_case_list_by_user(diagnose_repository, configuration_repository):
    config1 = DisplayConfig(user_email="user1@test.com", case_id=1, path_config={"key": "value"})
    configuration_repository.save_configuration(config1)

    config2 = DisplayConfig(user_email="user2@test.com", case_id=2, path_config={"key": "value"})
    configuration_repository.save_configuration(config2)

    diagnose1 = Answer(
        task_id=config1.id,
        case_id=1,
        user_email="user1@test.com",
        display_configuration=[],
    )
    diagnose_repository.add_answer(diagnose1)

    diagnose2 = Answer(
        task_id=config2.id,
        case_id=2,
        user_email="user2@test.com",
        display_configuration=[],
    )
    diagnose_repository.add_answer(diagnose2)

    user1_task_ids = diagnose_repository.get_answered_case_list_by_user("user1@test.com")
    user2_task_ids = diagnose_repository.get_answered_case_list_by_user("user2@test.com")

    assert user1_task_ids == [config1.id]
    assert user2_task_ids == [config2.id]

    diagnose3 = Answer(
        task_id=config1.id,
        case_id=3,
        user_email="user1@test.com",
        display_configuration=[],
    )
    diagnose_repository.add_answer(diagnose3)

    user1_task_ids = diagnose_repository.get_answered_case_list_by_user("user1@test.com")
    assert user1_task_ids == [config1.id, config1.id]
