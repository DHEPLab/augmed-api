import json

from flask import Blueprint, jsonify, request

from src.user.controller.request.loginRequest import LoginRequest
from src.user.repository.user_repository import UserRepository
from src.user.service.auth_service import AuthService

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

user_repository = UserRepository()

auth_service = AuthService(user_repository=user_repository)


@auth_blueprint.route("/login", methods=["POST"])
def login():
    req_data = request.get_json()
    login_request = LoginRequest(email=req_data["email"], password=req_data["password"])
    login_response = auth_service.login(login_request)
    return jsonify(json.loads(login_response.to_json())), 200
