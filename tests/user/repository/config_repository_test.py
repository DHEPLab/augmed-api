import pytest
from src.user.repository.config_repository import ConfigRepository
from src.user.model.config import Config

@pytest.fixture(scope="session")
def config_repository(session):
    return ConfigRepository(session)

@pytest.fixture(autouse=True)
def setup_database(session):
    session.query(Config).delete()
    session.commit()

def test_replace_from_blank_to_non_blank(config_repository: ConfigRepository ):
    assert config_repository.get_all_configurations() == []

    new_configs = [{'user_id': 1, 'case_id': 1, 'path_config': {'info': 'details'}}]
    config_repository.replace_all_configurations(new_configs)
    assert len(config_repository.get_all_configurations()) == 1

def test_replace_with_case_change(config_repository: ConfigRepository):
    # Initial configuration for user 1, case 1
    initial_configs = [{'user_id': 1, 'case_id': 1, 'path_config': {'info': 'initial'}}]
    config_repository.replace_all_configurations(initial_configs)

    # Replace configuration for the same user but different case
    new_configs = [{'user_id': 1, 'case_id': 2, 'path_config': {'info': 'updated'}}]
    config_repository.replace_all_configurations(new_configs)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].case_id == 2
    assert all_configs[0].path_config['info'] == 'updated'

def test_replace_to_more_configurations(config_repository: ConfigRepository):
    initial_configs = [{'user_id': 1, 'case_id': 1, 'path_config': {'info': 'initial'}}]
    config_repository.replace_all_configurations(initial_configs)

    new_configs = [
        {'user_id': 1, 'case_id': 1, 'path_config': {'info': 'same user, same case'}},
        {'user_id': 2, 'case_id': 1, 'path_config': {'info': 'new user, same case'}}
    ]
    config_repository.replace_all_configurations(new_configs)

    assert len(config_repository.get_all_configurations()) == 2

def test_replace_to_fewer_configurations(config_repository: ConfigRepository):
    # Initial configurations
    initial_configs = [
        {'user_id': 1, 'case_id': 1, 'path_config': {'info': 'one'}},
        {'user_id': 1, 'case_id': 2, 'path_config': {'info': 'two'}}
    ]
    config_repository.replace_all_configurations(initial_configs)

    new_configs = [{'user_id': 1, 'case_id': 1, 'path_config': {'info': 'remaining'}}]
    config_repository.replace_all_configurations(new_configs)

    all_configs = config_repository.get_all_configurations()
    assert len(all_configs) == 1
    assert all_configs[0].case_id == 1
    assert all_configs[0].path_config['info'] == 'remaining'

def test_path_config_from_value_to_blank(config_repository: ConfigRepository):
    # Start with a non-blank path_config
    initial_config = [{'user_id': 1, 'case_id': 1, 'path_config': {'info': 'initial data'}}]
    config_repository.replace_all_configurations(initial_config)

    # Check initial state
    config = config_repository.get_all_configurations()
    assert len(config) == 1
    assert config[0].path_config == {'info': 'initial data'}

    # Update to a blank path_config
    updated_config = [{'user_id': 1, 'case_id': 1, 'path_config': {}}]
    config_repository.replace_all_configurations(updated_config)

    # Check updated state
    updated = config_repository.get_all_configurations()
    assert len(updated) == 1
    assert updated[0].path_config == {}