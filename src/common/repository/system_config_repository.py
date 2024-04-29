from src.common.model.system_config import SystemConfig


class SystemConfigRepository:

    def __init__(self, session):
        self.session = session

    def get_config_by_id(self, config_id):
        return self.session.get(SystemConfig, config_id)
