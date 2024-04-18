import os
import time

import pytest
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate, upgrade
from testcontainers.postgres import PostgresContainer

from src import create_app, db


@pytest.fixture(scope="session")
def app():
    postgres = PostgresContainer("postgres", port=5432)
    postgres.start()
    time.sleep(3)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    migrations_dir = os.path.join(base_dir, 'src', 'migrations')

    app = create_app(
        dict(
            SQLALCHEMY_DATABASE_URI=postgres.get_connection_url(),
            JWT_SECRET_KEY='super-secret-key',
            JWT_ACCESS_TOKEN_EXPIRES=15 * 60,
            JWT_REFRESH_TOKEN_EXPIRES=259200
        )
    )
    JWTManager(app)
    with app.app_context():
        Migrate(app, db, directory=migrations_dir)
        upgrade()

        yield app
        db.session.remove()
        postgres.stop()


@pytest.fixture(scope="session")
def session(app):
    with app.app_context():
        return db.session


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def cleanup(request, session):
    def function_ends():
        session.rollback()
        session.close()

    request.addfinalizer(function_ends)
