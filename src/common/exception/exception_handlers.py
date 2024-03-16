from flask import jsonify
from flask_json_schema import JsonValidationError
from werkzeug.exceptions import (BadRequest, Forbidden, InternalServerError,
                                 NotFound, Unauthorized)

from common.model.ApiResponse import ApiResponse
from common.model.ErrorCode import ErrorCode


def register_error_handlers(app):
    @app.errorhandler(InternalServerError)
    def handle_application_exception(error):
        return jsonify(ApiResponse.fail(ErrorCode.INTERNAL_ERROR, str(error))), 500

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify(ApiResponse.fail(ErrorCode.BAD_REQUEST, str(error))), 400

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        return jsonify(ApiResponse.fail(ErrorCode.UNAUTHORIZED, str(error))), 401

    @app.errorhandler(Forbidden)
    def handle_forbidden(error):
        return jsonify(ApiResponse.fail(ErrorCode.FORBIDDEN, str(error))), 403

    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return jsonify(ApiResponse.fail(ErrorCode.NOT_FOUND, str(error))), 404

    @app.errorhandler(JsonValidationError)
    def validation_error(ex):
        return (
            jsonify(ApiResponse.fail(ErrorCode.INVALID_PARAMETER, str(ex))),
            ErrorCode.INVALID_PARAMETER.value,
        )
