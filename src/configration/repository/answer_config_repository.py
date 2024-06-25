from src.configration.model.answer_config import AnswerConfig


class AnswerConfigurationRepository:
    def __init__(self, session):
        self.session = session

    def add_answer_config(self, answer_config: AnswerConfig):
        self.session.add(answer_config)
        self.session.flush()

        return answer_config

    def query_latest_answer_config(self) -> AnswerConfig:
        answer_config = (
            self.session.query(AnswerConfig)
            .order_by(AnswerConfig.created_timestamp.desc())
            .first()
        )

        return answer_config
