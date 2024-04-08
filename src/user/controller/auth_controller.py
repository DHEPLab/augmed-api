from flask import Blueprint, Response, json, request, jsonify

from src import db
from src.common.model.ApiResponse import ApiResponse
from src.user.controller.request.loginRequest import LoginRequest
from src.user.controller.request.signupRequest import SignupRequest
from src.user.repository.user_repository import UserRepository
from src.user.service.auth_service import AuthService
from src.user.utils.auth_utils import jwt_validation_required

auth_blueprint = Blueprint("auth", __name__)

user_repository = UserRepository(db.session)

auth_service = AuthService(user_repository=user_repository)


@auth_blueprint.route("/auth/login", methods=["POST"])
def login() -> Response:
    req_data = request.get_json()
    login_request = LoginRequest(email=req_data["email"], password=req_data["password"])
    login_response = auth_service.login(login_request)

    response = json.jsonify(message="Login Successfully")
    response.status_code = 200

    response.headers["Authorization"] = f"Bearer {login_response.access_token}"
    return response


@auth_blueprint.route("/auth/signup", methods=["POST"])
def signup() -> Response:
    req_data = request.get_json()
    signup_request = SignupRequest(
        email=req_data["email"], password=req_data["password"]
    )

    auth_service.signup(signup_request)

    response = json.jsonify(ApiResponse.success("Sign up successfully"))
    response.status_code = 201

    return response

@auth_blueprint.route("/case", methods=["GET"])
@jwt_validation_required()
def get_case():
    return (
        jsonify([
            {
                "id": "003-v112022",
                "patient_chief_complaint": "Chest Pain",
                "age": 52,
                "sex": "Male"
            },
            {
                "id": "001-v103979",
                "patient_chief_complaint": "Polyuria",
                "age": 63,
                "sex": "Female"
            },
            {
                "id": "003-v112052",
                "patient_chief_complaint": "Chest Pain",
                "age": 44,
                "sex": "Male"
            },
            {
                "id": "003-v112082",
                "patient_chief_complaint": "Chest Pain",
                "age": 33,
                "sex": "Female"
            },
            {
                "id": "003-v112092",
                "patient_chief_complaint": "Chest Pain",
                "age": 22,
                "sex": "Male"
            }
        ]
        ),
        200,)
