from flask import Blueprint, jsonify, request

from src.user.controller.request.loginRequest import \
    LoginRequest  # Assuming your data classes are defined here
from src.user.service.auth_service import \
    AuthService  # Assuming AuthService is in this path

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

auth_service = AuthService()


@auth_blueprint.route("/login", methods=["POST"])
def login():
    req_data = request.get_json()
    login_request = LoginRequest(email=req_data["email"], password=req_data["password"])
    login_response = auth_service.login(login_request)

    return (
        jsonify(
            access_token=login_response.access_token,
            refresh_token=login_response.refresh_token,
        ),
        200,
    )
