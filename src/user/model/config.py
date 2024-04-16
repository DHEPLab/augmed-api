from src import db


class Config(db.Model):
    __tablename__ = "configurations"
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    case_id: int = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    path_config: object = db.Column(db.JSON, nullable=False)
