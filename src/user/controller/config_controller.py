from io import BytesIO

from flask import Blueprint, jsonify, request

from src import db
from src.common.exception.BusinessException import BusinessExceptionEnum
from src.common.model.ApiResponse import ApiResponse
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.service.configuration_service import ConfigurationService
from src.user.utils.auth_utils import jwt_validation_required

config_blueprint = Blueprint("config", __name__)
config_repository = ConfigurationRepository(db.session)
config_service = ConfigurationService(repository=config_repository)


@config_blueprint.route("/config/upload", methods=["POST"])
@jwt_validation_required()
def upload_config():
    if "file" not in request.files:
        return jsonify(ApiResponse.fail(BusinessExceptionEnum.NoFilePart)), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify(ApiResponse.fail(BusinessExceptionEnum.NoFileSelected)), 400

    if not allowed_file(file.filename):
        return (
            jsonify(ApiResponse.fail(BusinessExceptionEnum.InvalidFileExtension)),
            400,
        )

    file_stream = BytesIO(file.read())
    response_data = config_service.process_excel_file(file_stream)
    return jsonify(ApiResponse.success(response_data)), 200


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["xlsx", "xls"]
