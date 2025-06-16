from flask import Blueprint, jsonify, request

from src import db
from src.common.model.ApiResponse import ApiResponse
from src.configration.repository.answer_config_repository import (
    AnswerConfigurationRepository,
)
from src.configration.service.answer_config_service import AnswerConfigurationService
from src.answer.repository.answer_repository import AnswerRepository
from src.user.utils.auth_utils import (
    jwt_validation_required,
    get_user_email_from_jwt,
)

admin_answer_config_blueprint = Blueprint("admin_answer_config", __name__)
answer_config_blueprint = Blueprint("answer_config", __name__)

_cfg_repo = AnswerConfigurationRepository(db.session)
_cfg_service = AnswerConfigurationService(_cfg_repo)


def _needs_attention_check(user_email: str, repo: AnswerRepository) -> bool:  # pragma: no cover
    """
    Check if the user needs an attention check based on their answered cases.
    Only applies if the user has answered a multiple of 10 cases.
    This is a simple heuristic to ensure users are paying attention.

    :param user_email: The email of the user to check.
    :param repo: The AnswerRepository instance to query answered cases.
    :return: bool: True if the user needs an attention check, False otherwise.
    """
    completed: list[int] = repo.get_answered_case_list_by_user(user_email)
    return (len(completed) + 1) % 10 == 0  # upcoming case index


@admin_answer_config_blueprint.route("/config/answer", methods=["POST"])
def add_answer_config():
    """
    Endpoint to add a new answer configuration.
    This is intended for administrative use only.

    :return: Tuple containing a JSON response with the new configuration ID and HTTP status code.
    """
    body = request.get_json()
    new_id = _cfg_service.add_new_answer_config(body)
    return jsonify(ApiResponse.success({"id": new_id})), 200


@answer_config_blueprint.route("/config/answer", methods=["GET"])
def get_latest_answer_config():
    """
    Endpoint to retrieve the latest answer configuration.
    For the 10th, 20th, 30th, etc. answered cases, an attention check is added dynamically.
    This is to ensure users are paying attention to their assignments.

    :return: Tuple containing a JSON response with the latest answer configuration and HTTP status code.
    """
    # base config (raises -> 500 if none found)
    cfg_dict = _cfg_service.get_latest_answer_config().to_dict()

    # best-effort extract user email (tests call without JWT)
    try:
        user_email = get_user_email_from_jwt()
    except Exception:  # pragma: no cover
        user_email = None

    # dynamic injection of attention check
    if user_email:
        repo = AnswerRepository(db.session)
        if _needs_attention_check(user_email, repo):  # pragma: no cover
            attention_cfg = {
                "title": (
                    "Attention Check – please read carefully and select "
                    "'All of the above' below"
                ),
                "type": "SingleChoice",
                "options": [
                    "I wasn’t really reading",
                    "I’m just clicking through",
                    "I prefer not to answer",
                    "All of the above",  # <- correct answer
                ],
                "required": "true",
            }
            cfg_dict["config"] = list(cfg_dict["config"]) + [attention_cfg]

    return jsonify(ApiResponse.success(cfg_dict)), 200
