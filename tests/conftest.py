import time

import pytest
from testcontainers.postgres import PostgresContainer

from src import create_app, db


# TODO test app can start with testcontainers

@pytest.fixture(scope="session")
def app():
    postgres = PostgresContainer("postgres", port=5432)
    postgres.start()
    time.sleep(3)

    app = create_app(
        dict(SQLALCHEMY_DATABASE_URI=postgres.get_connection_url())
    )
    # alembic = Alembic()
    # alembic.init_app(app)
    with app.app_context():
        db.create_all()
        # alembic.upgrade()
        yield app
        db.session.remove()
        db.drop_all()
        postgres.stop()


@pytest.fixture(scope="session")
def session(app):
    with app.app_context():
        return db.session
