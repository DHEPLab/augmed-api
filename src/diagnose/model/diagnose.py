from datetime import datetime
from typing import List

from src import db
from src.diagnose.model.diagosis import Diagnosis


class Diagnose(db.Model):
    __tablename__ = "diagnose"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id: int = db.Column(db.Integer, nullable=True)
    case_id: int = db.Column(db.Integer, nullable=True)
    user_email: str = db.Column(db.String(128), nullable=True)
    display_configuration = db.Column(db.JSON, nullable=True)
    diagnosis: List[Diagnosis] = db.Column(db.JSON, nullable=False)
    other = db.Column(db.String(1024), nullable=True)

    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
