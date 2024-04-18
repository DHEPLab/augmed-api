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
        return

    def get_all_configurations(self):
        return self.session.query(Configuration).all()
