from flask_json_schema import JsonSchema, JsonValidationError

from src import create_app
from src.common.model.ApiResponse import ApiResponse
from src.common.model.ErrorCode import ErrorCode

app = create_app()
schema = JsonSchema(app)


@app.errorhandler(JsonValidationError)
def validation_error(e):
    return ApiResponse.fail(
        ErrorCode.INVALID_PARAMETER,
        ",".join(map(lambda error: error.message, e.errors)),
    )


if __name__ == "__main__":
    app.run(debug=True)
