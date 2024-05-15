import pytest

from src.user.model.configuration import Configuration
from src.user.repository.configuration_repository import ConfigurationRepository


@pytest.fixture
def config_repository(session):
    repo = ConfigurationRepository(session)
    session.query(Configuration).delete()
    session.commit()
    return repo


def test_clean_configurations(config_repository):
    config_repository.save_configuration(
        Configuration(user_email='usera@example.com', case_id=1, path_config={'info': 'initial'}))
    config_repository.save_configuration(
        Configuration(user_email='usera@example.com', case_id=2, path_config={'info': 'second'}))
    assert len(config_repository.get_all_configurations()) == 2

    config_repository.clean_configurations()
    assert len(config_repository.get_all_configurations()) == 0


def test_save_configuration(config_repository):
    # Test saving a single configuration
    new_config = Configuration(user_email='usera@example.com', case_id=1, path_config={'info': 'details'})
    config_repository.save_configuration(new_config)
    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].user_email == 'usera@example.com'
    assert all_configs[0].case_id == 1
    assert all_configs[0].path_config == {'info': 'details'}


def test_save_multiple_configurations(config_repository):
    # Saving multiple configurations
    configs = [
        Configuration(user_email='usera@example.com', case_id=1, path_config={'info': 'first'}),
        Configuration(user_email='usera@example.com', case_id=2, path_config={'info': 'second'})
    ]
    for config in configs:
        config_repository.save_configuration(config)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 2
    # Check details of one of the configurations
    assert any(
        config.user_email == 'usera@example.com' and config.case_id == 1 and config.path_config == {'info': 'first'} for
        config in all_configs)


def test_get_configuration_by_id(config_repository):
    new_config = Configuration(user_email='usera@example.com', case_id=1, path_config={'info': 'details'})
    config_repository.save_configuration(new_config)
    found = config_repository.get_configuration_by_id(new_config.id)

    assert found.__eq__(new_config)


def test_get_case_configurations_by_user_empty(config_repository):
    assert config_repository.get_case_configurations_by_user('usera@example.com') == []


def test_get_case_configurations_by_user_single_user_multiple_configs(config_repository):
    configs = [
        Configuration(user_email='usera@example.com', case_id=1, ),
        Configuration(user_email='usera@example.com', case_id=2, )
    ]
    for config in configs:
        config_repository.save_configuration(config)

    result = config_repository.get_case_configurations_by_user('usera@example.com')
    assert result.__len__() == 2
    assert result[0].__eq__(configs[0])
    assert result[1].__eq__(configs[1])


def test_should_avoid_duplicate_configurations(config_repository):
    config = Configuration(user_email='usera@example.com', case_id=1)
    config_repository.save_configuration(config)
    first_save_result = config_repository.get_case_configurations_by_user('usera@example.com')
    config_repository.save_configuration(config)
    second_save_result = config_repository.get_case_configurations_by_user('usera@example.com')
    assert first_save_result.__eq__(second_save_result)


def should_generate_same_configuration_id_for_same_configuration(config_repository):
    config = Configuration(user_email='usera@example.com', case_id=1)
    config_id = config.id

    new_config = Configuration(user_email='usera@example.com', case_id=1)
    new_config_id = config_repository.get_configuration_by_id(config.id)
    assert config_id.__eq__(new_config_id)
