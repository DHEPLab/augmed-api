from flask import Blueprint, jsonify

healthcheck_blueprint = Blueprint("healthcheck", __name__)


@healthcheck_blueprint.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "OK", "message": "Service is up and running."})
