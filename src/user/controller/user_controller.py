from flask import Blueprint, jsonify, request

from common.model.ErrorCode import ErrorCode
from src import db, schema
from src.common.model.ApiResponse import ApiResponse
from src.user.controller.request.CreateUserRequest import CreateUserRequest
from src.user.controller.schema.create_users_schema import create_users_schema
from src.user.service.user_service import UserService
from user.repository.user_repository import UserRepository

user_blueprint = Blueprint("user", __name__)

user_service = UserService(UserRepository(db.session))


@user_blueprint.route("/users", methods=["POST"])
@schema.validate(create_users_schema)
def create_user():
    data = CreateUserRequest.from_dict(request.get_json())
    response = user_service.add_inactive_user(data.users)
    return (
        ApiResponse.success(response),
        201,
    )


@user_blueprint.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = user_service.get_user(user_id)
    if user:
        return jsonify(ApiResponse.success({
            "name": user.name,
            "email": user.email
        })), 200
    else:
        return jsonify(ApiResponse.fail(ErrorCode.NOT_FOUND)), 404
