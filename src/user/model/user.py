from datetime import datetime

from src import db


class User(db.Model):
    db.metadata.clear()
    __tablename__ = "user"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(128), nullable=True)
    email: str = db.Column(db.String(128), nullable=False, unique=True)
    password: str = db.Column(db.String(192), nullable=True)
    salt: str = db.Column(db.String(192), nullable=True)
    admin_flag: str = db.Column(db.Boolean, default=False)
    position: str = db.Column(db.String(512), nullable=True)
    employer: str = db.Column(db.String(512), nullable=True)
    area_of_clinical_ex: str = db.Column(db.String(512), nullable=True)
    active: bool = db.Column(db.Boolean, default=False)
    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def copy(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self
