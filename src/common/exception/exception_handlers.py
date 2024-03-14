from werkzeug.exceptions import (BadRequest, Forbidden, InternalServerError,
                                 NotFound, Unauthorized)

from common.model.ApiResponse import ApiResponse


def register_error_handlers(app):
    @app.errorhandler(InternalServerError)
    def handle_application_exception(error):
        return ApiResponse.fail(error), 500

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return ApiResponse.fail(error.message), 400

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        return ApiResponse.fail(error.message), 401

    @app.errorhandler(Forbidden)
    def handle_forbidden(error):
        return ApiResponse.fail(error.message), 403

    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return ApiResponse.fail(error.message), 404
