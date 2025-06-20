from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float
from src import db


class Analytics(db.Model):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(128), nullable=False)
    case_config_id = Column(String, nullable=False)
    case_id = Column(Integer, nullable=False)

    # these three fields will also accept and store tz-aware UTC datetimes
    case_open_time = Column(DateTime(timezone=True), nullable=False)
    answer_open_time = Column(DateTime(timezone=True), nullable=False)
    answer_submit_time = Column(DateTime(timezone=True), nullable=False)

    to_answer_open_secs = Column(Float, nullable=False)
    to_submit_secs = Column(Float, nullable=False)
    total_duration_secs = Column(Float, nullable=False)

    created_timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    modified_timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        # ensure only one analytics row per case_config_id per user
        db.UniqueConstraint("user_email", "case_config_id"),
    )
