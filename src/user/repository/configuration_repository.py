from typing import List, Tuple

from src.user.model.configuration import Configuration


class ConfigurationRepository:

    def __init__(self, session):
        self.session = session

    def clean_configurations(self):
        self.session.query(Configuration).delete()
        self.session.flush()

    def save_configuration(self, config: Configuration):
        self.session.add(config)
        self.session.flush()
        return config

    def get_all_configurations(self):
        return self.session.query(Configuration).all()

    def get_configuration_by_id(self, config_id):
        return self.session.get(Configuration, config_id)

    def get_case_configurations_by_user(self, user_email: str) -> List[Tuple[int, str]]:
        configurations = (
            self.session.query(Configuration.case_id, Configuration.id)
            .filter(Configuration.user_email == user_email)
            .all()
        )

        return [(config.case_id, config.id) for config in configurations]
