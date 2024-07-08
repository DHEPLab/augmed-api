from flask import Blueprint, jsonify, request

from src import db
from src.common.model.ApiResponse import ApiResponse
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.configration.service.answer_config_service import \
    AnswerConfigurationService

admin_answer_config_blueprint = Blueprint("admin_answer_config", __name__)
answer_config_blueprint = Blueprint("answer_config", __name__)

answer_repository = AnswerConfigurationRepository(db.session)
answer_service = AnswerConfigurationService(answer_repository)


@admin_answer_config_blueprint.route("/config/answer", methods=["POST"])
def add_answer_config():
    body = request.get_json()

    id = answer_service.add_new_answer_config(body)

    return (
        jsonify(ApiResponse.success({"id": id})),
        200,
    )


@answer_config_blueprint.route("/config/answer", methods=["GET"])
def get_latest_answer_config():
    answer_config = answer_service.get_latest_answer_config().to_dict()

    return (
        jsonify(ApiResponse.success(answer_config)),
        200,
    )
