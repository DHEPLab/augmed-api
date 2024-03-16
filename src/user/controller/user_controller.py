from flask import Blueprint, jsonify, request

from src import db, schema
from src.common.model.ApiResponse import ApiResponse
from src.common.model.ErrorCode import ErrorCode
from src.user.controller.schema.create_users_schema import create_users_schema
from src.user.model.user import User
from src.user.repository.user_repository import UserRepository
from src.user.service.user_service import UserService

user_blueprint = Blueprint("user", __name__)

user_service = UserService(UserRepository(db.session))


@user_blueprint.route("/users", methods=["POST"])
@schema.validate(create_users_schema)
def create_user():
    body = request.get_json()
    users = map(
        lambda user_input: User(
            name=user_input.get("name"),
            email=user_input.get("email"),
            position=user_input.get("position"),
            employer=user_input.get("employer"),
            area_of_clinical_ex=user_input.get("area_of_clinical_ex"),
        ),
        body["users"],
    )
    response = user_service.add_inactive_user(users)
    return (
        jsonify(ApiResponse.success(response)),
        201,
    )


@user_blueprint.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = user_service.get_user(user_id)
    if user:
        return (
            jsonify(ApiResponse.success({"name": user.name, "email": user.email})),
            200,
        )
    else:
        return jsonify(ApiResponse.fail(ErrorCode.NOT_FOUND)), 404
