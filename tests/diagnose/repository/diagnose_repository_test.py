import pytest

from src.diagnose.model.diagnose import Diagnose
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.user.model.configuration import Configuration
from src.user.repository.configuration_repository import ConfigurationRepository


@pytest.fixture
def diagnose_repository(session):
    return DiagnoseRepository(session)


@pytest.fixture
def configuration_repository(session):
    return ConfigurationRepository(session)


def test_add_diagnose(diagnose_repository, configuration_repository):
    config = Configuration(user_email="user@test.com", case_id=1, path_config={"key": "value"})
    configuration_repository.save_configuration(config)

    diagnose = Diagnose(
        task_id=config.id,
        case_id=1,
        user_email="user@test.com",
        display_configuration=[],
        diagnosis=[],
        other=""
    )

    assert diagnose.id is None

    diagnose_repository.add_diagnose(diagnose)

    assert diagnose.id is not None


def test_get_diagnosed_case_list_by_user(diagnose_repository, configuration_repository):
    config1 = Configuration(user_email="user1@test.com", case_id=1, path_config={"key": "value"})
    configuration_repository.save_configuration(config1)

    config2 = Configuration(user_email="user2@test.com", case_id=2, path_config={"key": "value"})
    configuration_repository.save_configuration(config2)

    diagnose1 = Diagnose(
        task_id=config1.id,
        case_id=1,
        user_email="user1@test.com",
        display_configuration=[],
        diagnosis=[],
        other=""
    )
    diagnose_repository.add_diagnose(diagnose1)

    diagnose2 = Diagnose(
        task_id=config2.id,
        case_id=2,
        user_email="user2@test.com",
        display_configuration=[],
        diagnosis=[],
        other=""
    )
    diagnose_repository.add_diagnose(diagnose2)

    user1_task_ids = diagnose_repository.get_diagnosed_case_list_by_user("user1@test.com")
    user2_task_ids = diagnose_repository.get_diagnosed_case_list_by_user("user2@test.com")

    assert user1_task_ids == [config1.id]
    assert user2_task_ids == [config2.id]

    diagnose3 = Diagnose(
        task_id=config1.id,
        case_id=3,
        user_email="user1@test.com",
        display_configuration=[],
        diagnosis=[],
        other=""
    )
    diagnose_repository.add_diagnose(diagnose3)

    user1_task_ids = diagnose_repository.get_diagnosed_case_list_by_user("user1@test.com")
    assert user1_task_ids == [config1.id, config1.id]
