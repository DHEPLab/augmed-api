import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from src import db


class DiagnoseConfig(db.Model):
    __tablename__ = "diagnose_config"

    id: str = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config: str = db.Column(db.JSON, nullable=False)
    created_timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)
