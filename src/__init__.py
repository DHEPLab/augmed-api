from flask import Flask
from flask_json_schema import JsonSchema
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from common.exception.exception_handlers import register_error_handlers

db = SQLAlchemy()
schema = JsonSchema()


def create_app(config_object=None):
    app = Flask(__name__)

    # Allow custom configuration for testing
    if config_object:
        app.config.from_mapping(config_object)
    else:
        # Default configuration setup from config.py
        app.config.from_object("src.config.Config")

    schema.init_app(app)
    try:
        db.init_app(app)
        Migrate(app, db)

    except RuntimeError:
        print(
            "Database connection failed. Continuing without database."
        )  # todo: Remove after db setup

    with app.app_context():
        # Import Blueprints after initializing db to avoid circular import
        from src.health.healthCheckController import healthcheck_blueprint
        from src.user.controller.authController import auth_blueprint
        from src.user.controller.user_controller import user_blueprint

        app.register_blueprint(user_blueprint, url_prefix="/api")
        app.register_blueprint(auth_blueprint, url_prefix="/api")
        app.register_blueprint(healthcheck_blueprint, url_prefix="/api")

        register_error_handlers(app)

    return app
