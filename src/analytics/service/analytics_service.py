from datetime import datetime, timezone

from src.analytics.model.analytics import Analytics
from src.analytics.repository.analytics_repository import AnalyticsRepository
from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
from src.user.utils.auth_utils import get_user_email_from_jwt
from src.user.repository.display_config_repository import DisplayConfigRepository


class AnalyticsService:
    """
    High-level service that records timing metrics for a user’s case review.
    Uses an UPSERT, so repeated calls for the same (user_email, case_config_id)
    update the existing Analytics row instead of throwing UniqueViolation.
    """

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        display_config_repository: DisplayConfigRepository,
    ):  # pragma: no cover
        self.analytics_repo = analytics_repository
        self.config_repo = display_config_repository

    # ------------------------------------------------------------------ #
    def record_metrics(
        self,
        case_config_id: str,
        case_open: datetime,
        answer_open: datetime,
        answer_submit: datetime,
    ) -> Analytics:  # pragma: no cover
        """Validate ownership, compute durations, then upsert Analytics."""
        user_email: str = get_user_email_from_jwt()

        # confirm caller owns this config
        config = self.config_repo.get_configuration_by_id(case_config_id)
        if not config or config.user_email != user_email:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        # durations (sec)
        to_answer_open = (answer_open - case_open).total_seconds()
        to_submit = (answer_submit - answer_open).total_seconds()
        total = (answer_submit - case_open).total_seconds()
        now = datetime.now(timezone.utc)

        analytics = Analytics(
            user_email=user_email,
            case_config_id=case_config_id,
            case_id=config.case_id,
            case_open_time=case_open,
            answer_open_time=answer_open,
            answer_submit_time=answer_submit,
            to_answer_open_secs=to_answer_open,
            to_submit_secs=to_submit,
            total_duration_secs=total,
            created_timestamp=now,
            modified_timestamp=now,
        )

        # use UPSERT instead of plain add()
        return self.analytics_repo.add_or_update(analytics)
