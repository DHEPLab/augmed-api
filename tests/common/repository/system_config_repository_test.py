import pytest

from src.common.model.system_config import SystemConfig
from src.common.repository.system_config_repository import SystemConfigRepository


@pytest.fixture
def system_config_repository(session):
    return SystemConfigRepository(session)


def test_clean_configurations(session, system_config_repository):
    config = SystemConfig(
        id='page_config',
        json_config={}
    )
    session.add(config)
    session.flush()

    found = system_config_repository.get_config_by_id(config.id)

    assert found == config

