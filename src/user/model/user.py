from datetime import datetime

from src import db


class User(db.Model):
    db.metadata.clear()
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(192), nullable=True)
    salt = db.Column(db.String(192), nullable=True)
    admin_flag = db.Column(db.Boolean, default=False)
    position = db.Column(db.String(128), nullable=True)
    employer = db.Column(db.String(128), nullable=True)
    area_of_clinical_ex = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Boolean, default=False)
    created_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
