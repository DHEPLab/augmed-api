from flask import Blueprint, request, jsonify
from src import db
from src.analytics.service.analytics_service import AnalyticsService
from src.analytics.repository.analytics_repository import AnalyticsRepository
from src.user.repository.display_config_repository import DisplayConfigRepository
from src.common.model.ApiResponse import ApiResponse
from src.user.utils.auth_utils import jwt_validation_required
from src.common.exception.BusinessException import BusinessException, BusinessExceptionEnum
from datetime import datetime, timezone

# Give the blueprint its full prefix; no strict_slashes here
analytics_blueprint = Blueprint(
    "analytics",
    __name__,
    url_prefix="/api/analytics",
)

@analytics_blueprint.route("/", methods=["POST"], strict_slashes=False)
@jwt_validation_required()
def record():
    payload = request.get_json() or {}
    case_config_id    = payload.get("caseConfigId")
    case_open_str     = payload.get("caseOpenTime")
    answer_open_str   = payload.get("answerOpenTime")
    answer_submit_str = payload.get("answerSubmitTime")

    if not all([case_config_id, case_open_str, answer_open_str, answer_submit_str]):
        ex = BusinessException(
            BusinessExceptionEnum.RenderTemplateError,
            "Missing analytics metrics fields"
        )
        return jsonify(ApiResponse.error(ex)), 400

    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    try:
        case_open     = datetime.strptime(case_open_str, fmt).replace(tzinfo=timezone.utc)
        answer_open   = datetime.strptime(answer_open_str, fmt).replace(tzinfo=timezone.utc)
        answer_submit = datetime.strptime(answer_submit_str, fmt).replace(tzinfo=timezone.utc)
    except ValueError:
        ex = BusinessException(
            BusinessExceptionEnum.RenderTemplateError,
            "Bad timestamp format for analytics"
        )
        return jsonify(ApiResponse.error(ex)), 400

    analytics = AnalyticsService(
        analytics_repository=AnalyticsRepository(db.session),
        display_config_repository=DisplayConfigRepository(db.session),
    ).record_metrics(case_config_id, case_open, answer_open, answer_submit)

    db.session.commit()
    return jsonify(ApiResponse.success({"id": analytics.id})), 200
