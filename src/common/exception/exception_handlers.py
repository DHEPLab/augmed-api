from flask_json_schema import JsonValidationError
from werkzeug.exceptions import (BadRequest, Forbidden, InternalServerError,
                                 NotFound, Unauthorized)

from common.model.ApiResponse import ApiResponse
from common.model.ErrorCode import ErrorCode


def register_error_handlers(app):
    @app.errorhandler(InternalServerError)
    def handle_application_exception(error):
        return ApiResponse.fail(ErrorCode.INTERNAL_ERROR, error.message), 500

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return ApiResponse.fail(ErrorCode.BAD_REQUEST, error.message), 400

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        return ApiResponse.fail(ErrorCode.UNAUTHORIZED, error.message), 401

    @app.errorhandler(Forbidden)
    def handle_forbidden(error):
        return ApiResponse.fail(ErrorCode.FORBIDDEN, error.message), 403

    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return ApiResponse.fail(ErrorCode.NOT_FOUND, error.message), 404

    @app.errorhandler(JsonValidationError)
    def validation_error(ex):
        return (
            ApiResponse.fail(
                ErrorCode.INVALID_PARAMETER,
                ",".join(map(lambda error: error.message, ex.errors)),
            ),
            ErrorCode.INVALID_PARAMETER.value,
        )
