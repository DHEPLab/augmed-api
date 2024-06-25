from io import StringIO

from flask import Blueprint, jsonify, request

from src import db
from src.common.exception.BusinessException import BusinessExceptionEnum
from src.common.model.ApiResponse import ApiResponse
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.service.configuration_service import ConfigurationService
from src.user.utils.csv_parser import is_csv_file

config_blueprint = Blueprint("config", __name__)
config_repository = ConfigurationRepository(db.session)
config_service = ConfigurationService(repository=config_repository)


@config_blueprint.route("/config/upload", methods=["POST"])
def upload_config():
    if "file" not in request.files:
        return jsonify(ApiResponse.fail(BusinessExceptionEnum.NoFilePart)), 400

    file = request.files["file"]

    if not is_csv_file(file.filename):
        return (
            jsonify(ApiResponse.fail(BusinessExceptionEnum.InvalidFileExtension)),
            400,
        )

    file_stream = StringIO(file.read().decode())
    response_data = config_service.process_csv_file(file_stream)
    return jsonify(ApiResponse.success(response_data)), 200
