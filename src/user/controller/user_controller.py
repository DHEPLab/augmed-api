from flask import Blueprint, jsonify, request

from app import schema
from common.model.ApiResponse import ApiResponse
from src.user.service.user_service import UserService
from user.controller.request.CreateUserRequest import CreateUserRequest
from user.controller.schema.create_users_schema import create_users_schema

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/users", methods=["POST"])
@schema.validate(create_users_schema)
def create_user():
    data = CreateUserRequest.from_dict(request.get_json())
    response = UserService.add_inactive_user(data.users)
    return (
        ApiResponse.success(response),
        201,
    )


@user_blueprint.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = UserService.get_user(user_id)
    if user:
        return (
            jsonify(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "title": user.title,
                    "admin_flag": user.admin_flag,
                    "created_timestamp": user.created_timestamp,
                    "modified_timestamp": user.modified_timestamp,
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "User not found"}), 404
