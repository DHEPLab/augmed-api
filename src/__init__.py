from os import path

from flask import Flask
from flask_json_schema import JsonSchema
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

from src.common.exception.exception_handlers import register_error_handlers

db = SQLAlchemy()
schema = JsonSchema()
jwt = JWTManager()


def create_app(config_object=None):
    app = Flask(__name__)
    #
    # CORS(
    #     app,
    #     origins=["http://localhost:3000"],
    #     supports_credentials=True,
    #     expose_headers=["Authorization"],
    # )

    # Allow custom configuration for testing
    if config_object:
        app.config.from_mapping(config_object)
    else:
        # Default configuration setup from config.py
        # TODO: load from object not file ref.
        app.config.from_object("src.config.Config")

    schema.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    Migrate(
        app, db, directory=path.join(path.dirname(path.abspath(__file__)), "migrations")
    )

    with app.app_context():
        # comment db init to avoid failure, need change to migrate
        if not config_object:
            upgrade()

        # Import Blueprints after initializing db to avoid circular import
        from src.answer.controller.answer_controller import answer_blueprint
        from src.cases.controller.case_controller import case_blueprint
        from src.configration.controller.answer_config_controller import (
            admin_answer_config_blueprint, answer_config_blueprint)
        from src.health.healthCheckController import healthcheck_blueprint
        from src.user.controller.auth_controller import auth_blueprint
        from src.user.controller.config_controller import config_blueprint
        from src.user.controller.user_controller import user_blueprint
        from src.analytics.controller.analytics_controller import analytics_blueprint

        app.register_blueprint(admin_answer_config_blueprint, url_prefix="/admin")
        app.register_blueprint(user_blueprint, url_prefix="/admin")
        app.register_blueprint(config_blueprint, url_prefix="/admin")

        app.register_blueprint(answer_config_blueprint, url_prefix="/api")
        app.register_blueprint(auth_blueprint, url_prefix="/api")
        app.register_blueprint(healthcheck_blueprint, url_prefix="/api")
        app.register_blueprint(case_blueprint, url_prefix="/api")
        app.register_blueprint(answer_blueprint, url_prefix="/api")
        app.register_blueprint(analytics_blueprint)

        register_error_handlers(app)

    return app
