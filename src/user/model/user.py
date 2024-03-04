from datetime import datetime

from src import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    title = db.Column(db.String(128), nullable=True)
    password = db.Column(db.String(192), nullable=False)
    salt = db.Column(db.String(192), nullable=False)
    admin_flag = db.Column(db.Boolean, default=False)
    created_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
