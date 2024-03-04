from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuration setup from config.py
    app.config.from_object("src.config.Config")

    db.init_app(app)
    Migrate(app, db)  # Initialize Flask-Migrate

    with app.app_context():
        # Import Blueprints after initializing db to avoid circular import
        from src.user.controller.user_controller import user_blueprint

        app.register_blueprint(user_blueprint, url_prefix="/api")
    return app
