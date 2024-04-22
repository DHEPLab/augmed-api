from src import db


class Configuration(db.Model):
    __tablename__ = "configuration"
    id: int = db.Column(db.Integer, primary_key=True)
    user_email: str = db.Column(db.String)
    case_id: int = db.Column(db.Integer)
    path_config = db.Column(db.JSON, nullable=True)

    def __str__(self):
        return (
            f"Configuration(id={self.id}, user_id={self.user_email}, "
            f"case_id={self.case_id}, path_config={self.path_config})"
        )
