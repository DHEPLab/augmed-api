from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.analytics.model.analytics import Analytics


class AnalyticsRepository:
    """
    Handles persistence for Analytics.  add_or_update() performs a
    PostgreSQL ON CONFLICT … DO UPDATE to satisfy unique constraint
    uq_analytics_user_case without raising IntegrityError.
    """

    def __init__(self, session: Session):  # pragma: no cover
        self.session: Session = session

    def add_or_update(self, analytics: Analytics) -> Analytics:  # pragma: no cover
        """
        Insert OR update by (user_email, case_config_id).
        Returns the resulting Analytics ORM object attached to the session.
        """
        stmt = (
            insert(Analytics)
            .values(
                user_email=analytics.user_email,
                case_config_id=analytics.case_config_id,
                case_id=analytics.case_id,
                case_open_time=analytics.case_open_time,
                answer_open_time=analytics.answer_open_time,
                answer_submit_time=analytics.answer_submit_time,
                to_answer_open_secs=analytics.to_answer_open_secs,
                to_submit_secs=analytics.to_submit_secs,
                total_duration_secs=analytics.total_duration_secs,
                created_timestamp=analytics.created_timestamp,
                modified_timestamp=analytics.modified_timestamp,
            )
            .on_conflict_do_update(
                index_elements=["user_email", "case_config_id"],
                set_=dict(
                    case_id=analytics.case_id,
                    case_open_time=analytics.case_open_time,
                    answer_open_time=analytics.answer_open_time,
                    answer_submit_time=analytics.answer_submit_time,
                    to_answer_open_secs=analytics.to_answer_open_secs,
                    to_submit_secs=analytics.to_submit_secs,
                    total_duration_secs=analytics.total_duration_secs,
                    modified_timestamp=datetime.now(timezone.utc),
                ),
            )
            .returning(Analytics)
        )

        result = self.session.execute(stmt)
        self.session.flush()  # keep session state in sync
        return result.scalars().first()

    # ------------------------------------------------------------------ #
    # Legacy method retained for parts of the codebase that still expect
    # the old "add" contract (will raise on duplicate key).
    # ------------------------------------------------------------------ #
    def add(self, analytics: Analytics) -> Analytics:  # pragma: no cover
        self.session.add(analytics)
        self.session.flush()
        return analytics
