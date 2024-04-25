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

    def get_configuration_by_user_and_case(self, case_id, user_email):
        configuration = (
            self.session.query(Configuration)
            .filter(
                Configuration.user_email == user_email, Configuration.case_id == case_id
            )
            .first()
        )
        return configuration.path_config if configuration else None
