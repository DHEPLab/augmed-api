from src import db


class Config(db.Model):
    __tablename__ = "configurations"
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"))
    case_id: int = db.Column(
        db.Integer,
        db.ForeginKey("visit_occurrence.visit_occurrence_id"),
        nullable=False,
    )
    path_config: object = db.Column(db.JSON, nullable=False)
