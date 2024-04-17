from src.user.model.configurations import Configurations


class ConfigurationRepository:

    def __init__(self, session):
        self.session = session

    def replace_all_configurations(self, new_configurations):
        self.session.query(Configurations).delete(synchronize_session="fetch")

        for config in new_configurations:
            new_config = Configurations(
                user_id=config["user_id"],
                case_id=config["case_id"],
                path_config=config["path_config"],
            )
            self.session.add(new_config)

    def get_all_configurations(self):
        return self.session.query(Configurations).all()
