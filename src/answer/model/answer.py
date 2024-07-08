from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from src import db


class Answer(db.Model):
    __tablename__ = "answer"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id: str = db.Column(
        db.String,
        nullable=True,
    )
    case_id: int = db.Column(db.Integer, nullable=True)
    user_email: str = db.Column(db.String(128), nullable=True)
    display_configuration = db.Column(db.JSON, nullable=True)
    answer_config_id = db.Column(UUID(as_uuid=True), nullable=True)
    answer: dict = db.Column(db.JSON, nullable=True)

    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    __table_args__ = (db.UniqueConstraint("task_id", "case_id", "user_email"),)
