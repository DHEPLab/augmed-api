import json
import uuid

from src import db


class Configuration(db.Model):
    __tablename__ = "configuration"
    id = db.Column(db.String, primary_key=True)
    user_email = db.Column(db.String)
    case_id = db.Column(db.Integer)
    path_config = db.Column(db.JSON, nullable=True)

    def __init__(self, user_email, case_id, path_config=None):
        self.user_email = user_email
        self.case_id = case_id
        self.path_config = path_config
        self.id = self.generate_uuid()

    def generate_uuid(self):
        unique_string = f"{self.user_email}-{self.case_id}-{json.dumps(self.path_config, sort_keys=True)}"
        return uuid.uuid5(uuid.NAMESPACE_URL, unique_string).hex

    def to_dict(self):
        return {
            "user_email": self.user_email,
            "case_id": self.case_id,
            "path_config": self.path_config,
        }
