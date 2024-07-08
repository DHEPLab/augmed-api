import uuid
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import UUID

from src import db


class ResetPasswordToken(db.Model):
    __tablename__ = "reset_password_token"

    id: str = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: str = db.Column(db.String(128), nullable=False)
    token: str = db.Column(db.String(128), nullable=False)
    active: bool = db.Column(db.Boolean, default=True)
    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_timestamp: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expired_at: datetime = db.Column(
        db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=2)
    )
