from flask import Blueprint, jsonify, request

from src import db
from src.common.model.ApiResponse import ApiResponse
from src.configration.repository.answer_config_repository import \
    AnswerConfigurationRepository
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.diagnose.service.diagnose_service import DiagnoseService
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.utils.auth_utils import jwt_validation_required

diagnose_blueprint = Blueprint("diagnose", __name__)

diagnose_service = DiagnoseService(
    diagnose_repository=DiagnoseRepository(db.session),
    configuration_repository=ConfigurationRepository(db.session),
    answer_config_repository=AnswerConfigurationRepository(db.session),
)


@diagnose_blueprint.route("/diagnose/<string:task_id>", methods=["POST"])
@jwt_validation_required()
def add_diagnose_response(task_id):
    data = request.get_json()

    diagnose_response = diagnose_service.add_diagnose_response(task_id, data)

    return jsonify(ApiResponse.success({"id": diagnose_response.id})), 200
