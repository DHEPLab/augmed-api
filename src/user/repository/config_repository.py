from src.user.model.config import Config


class ConfigRepository:

    def __init__(self, session):
        self.session = session

    def replace_all_configurations(self, new_configurations):
        self.session.query(Config).delete(synchronize_session="fetch")

        for config in new_configurations:
            new_config = Config(
                user_id=config["user_id"],
                case_id=config["case_id"],
                path_config=config["path_config"],
            )
            self.session.add(new_config)
