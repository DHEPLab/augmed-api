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
    config_repository.save_configuration(Configuration(user_id=1, case_id=1, path_config={'info': 'initial'}))
    config_repository.save_configuration(Configuration(user_id=2, case_id=2, path_config={'info': 'second'}))
    assert len(config_repository.get_all_configurations()) == 2

    config_repository.clean_configurations()
    assert len(config_repository.get_all_configurations()) == 0

def test_save_configuration(config_repository):
    # Test saving a single configuration
    new_config = Configuration(user_id=1, case_id=1, path_config={'info': 'details'})
    config_repository.save_configuration(new_config)
    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].user_id == 1
    assert all_configs[0].case_id == 1
    assert all_configs[0].path_config == {'info': 'details'}

def test_save_multiple_configurations(config_repository):
    # Saving multiple configurations
    configs = [
        Configuration(user_id=1, case_id=1, path_config={'info': 'first'}),
        Configuration(user_id=2, case_id=2, path_config={'info': 'second'})
    ]
    for config in configs:
        config_repository.save_configuration(config)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 2
    # Check details of one of the configurations
    assert any(config.user_id == 1 and config.case_id == 1 and config.path_config == {'info': 'first'} for config in all_configs)


