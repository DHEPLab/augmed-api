from src import db


class DisplayConfig(db.Model):
    __tablename__ = "display_config"
    id = db.Column(db.String, primary_key=True)
    user_email = db.Column(db.String)
    case_id = db.Column(db.Integer)
    path_config = db.Column(db.JSON, nullable=True)

    def __init__(self, user_email, case_id, path_config=None, id=None):
        self.user_email = user_email
        self.case_id = case_id
        self.path_config = path_config
        self.id = id

    def to_dict(self):
        return {
            "user_email": self.user_email,
            "case_id": self.case_id,
            "path_config": self.path_config,
        }
