import pytest

from src.user.model.display_config import DisplayConfig
from src.user.repository.display_config_repository import DisplayConfigRepository


@pytest.fixture
def config_repository(session):
    repo = DisplayConfigRepository(session)
    session.query(DisplayConfig).delete()
    session.commit()
    return repo


def test_clean_configurations(config_repository):
    config_repository.save_configuration(
        DisplayConfig(
            user_email="usera@example.com", case_id=1, path_config={"info": "initial"}
        )
    )
    config_repository.save_configuration(
        DisplayConfig(
            user_email="usera@example.com", case_id=2, path_config={"info": "second"}
        )
    )
    assert len(config_repository.get_all_configurations()) == 2

    config_repository.clean_configurations()
    assert len(config_repository.get_all_configurations()) == 0


def test_save_configuration(config_repository):
    # Test saving a single configuration
    new_config = DisplayConfig(
        user_email="usera@example.com", case_id=1, path_config={"info": "details"}
    )
    config_repository.save_configuration(new_config)
    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].user_email == "usera@example.com"
    assert all_configs[0].case_id == 1
    assert all_configs[0].path_config == {"info": "details"}


def test_save_multiple_configurations(config_repository):
    # Saving multiple configurations
    configs = [
        DisplayConfig(
            user_email="usera@example.com", case_id=1, path_config={"info": "first"}
        ),
        DisplayConfig(user_email="usera@example.com", case_id=1, path_config=[]),
    ]
    for config in configs:
        config_repository.save_configuration(config)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 2
    # Check details of one of the configurations
    assert any(
        config.user_email == "usera@example.com"
        and config.case_id == 1
        and config.path_config == {"info": "first"}
        for config in all_configs
    )


def test_get_configuration_by_id(config_repository):
    new_config = DisplayConfig(
        user_email="usera@example.com", case_id=1, path_config={"info": "details"}
    )
    config_repository.save_configuration(new_config)
    found = config_repository.get_configuration_by_id(new_config.id)

    assert found.__eq__(new_config)


def test_get_case_configurations_by_user_empty(config_repository):
    assert config_repository.get_case_configurations_by_user("usera@example.com") == []


def test_get_case_configurations_by_user_single_user_multiple_configs(
    config_repository,
):
    configs = [
        DisplayConfig(
            user_email="usera@example.com",
            case_id=1,
        ),
        DisplayConfig(
            user_email="usera@example.com",
            case_id=2,
        ),
    ]
    for config in configs:
        config_repository.save_configuration(config)

    result = config_repository.get_case_configurations_by_user("usera@example.com")
    assert result.__len__() == 2
    assert result[0].__eq__(configs[0])
    assert result[1].__eq__(configs[1])


def test_should_avoid_duplicate_configurations(config_repository):
    config = DisplayConfig(user_email="usera@example.com", case_id=1)
    config_repository.save_configuration(config)
    first_save_result = config_repository.get_case_configurations_by_user(
        "usera@example.com"
    )
    config_repository.save_configuration(config)
    second_save_result = config_repository.get_case_configurations_by_user(
        "usera@example.com"
    )
    assert first_save_result.__eq__(second_save_result)


def test_should_generate_same_configuration_id_for_same_configuration(
    config_repository,
):
    config = config_repository.save_configuration(
        config=DisplayConfig(user_email="usera@example.com", case_id=1)
    )
    config_repository.clean_configurations()
    new_config_id = config_repository.save_configuration(
        DisplayConfig(user_email="usera@example.com", case_id=1)
    )
    assert config.id.__eq__(new_config_id)
