from src import db


class Configuration(db.Model):
    __tablename__ = "configuration"
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer)
    case_id: int = db.Column(db.Integer)
    path_config: object = db.Column(db.JSON, nullable=True)
