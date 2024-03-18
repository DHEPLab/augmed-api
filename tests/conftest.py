import time

import pytest
from flask_jwt_extended import JWTManager
from testcontainers.postgres import PostgresContainer

from src import create_app, db


@pytest.fixture(scope="session")
def app():
    postgres = PostgresContainer("postgres", port=5432)
    postgres.start()
    time.sleep(3)

    app = create_app(
        dict(
            SQLALCHEMY_DATABASE_URI=postgres.get_connection_url(),
            JWT_SECRET_KEY='super-secret-key',
            JWT_ACCESS_TOKEN_EXPIRES=3600,
            JWT_REFRESH_TOKEN_EXPIRES=3600,
        )
    )
    JWTManager(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
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
