import os

import pytest
from alembic import command
from flask_migrate import Config
from sqlalchemy.exc import IntegrityError

from src import create_app, db
from src.user.repository.user_repository import UserRepository  # Replace with your actual UserRepository import
from user.model.user import User


class TestConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


@pytest.fixture(scope='session')
def app():
    # Create a Flask application for testing
    app = create_app(config_object=TestConfig)

    # Define the location of the Alembic configuration file and migration scripts
    alembic_cfg_path = os.path.join(app.root_path, 'migrations', 'alembic.ini')

    # Set up the Alembic configuration
    alembic_cfg = Config(alembic_cfg_path)
    alembic_cfg.set_main_option('script_location', os.path.join(app.root_path, 'migrations'))
    alembic_cfg.set_main_option('sqlalchemy.url', TestConfig.SQLALCHEMY_DATABASE_URI)

    # Apply the migrations to the test database
    with app.app_context():
        # Apply the database migrations directly using Alembic
        command.upgrade(alembic_cfg, 'head')

    yield app


@pytest.fixture(scope='session')
def client(app):
    # Set up the Flask test client
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def _db(app):
    # Set up the database
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()


@pytest.fixture(scope='function')
def user_repository(_db):
    # Set up the UserRepository fixture
    return UserRepository(db=db)


@pytest.fixture(scope='module', autouse=True)
def setup_database(app):
    # Use the 'app' fixture to create an application context
    with app.app_context():
        # 在此上下文中添加测试数据到数据库
        user1 = User(name="Unique User", email="unique.email@email.com", password="password", salt="salt")
        user2 = User(name="Success User", email="success.email@email.com", password="password", salt="salt")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

    yield  # this will run before the test

    # Teardown test data after each test function
    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()


def test_create_user_success(user_repository, app):
    with app.app_context():
        new_user = User(name="New User", email="new.user@email.com", password="secret", salt="randomsalt")
        created_user = user_repository.create_user(new_user)
        assert created_user.id is not None
        assert created_user.email == "new.user@email.com"


def test_create_user_failed_due_to_duplicate_email(user_repository, app):
    with app.app_context():
        duplicated_email_user = User(name="Another Unique User", email="unique.email@email.com", password="password",
                                     salt="salt")
        with pytest.raises(IntegrityError):
            user_repository.create_user(duplicated_email_user)


def test_get_user_by_id_success(user_repository, app):
    with app.app_context():
        retrieved_user = user_repository.get_user_by_email("success.email@email.com")
        success_user_id = retrieved_user.id
        retrieved_by_id_user = user_repository.get_user_by_id(success_user_id)
        assert retrieved_by_id_user is not None
        assert retrieved_by_id_user.email == "success.email@email.com"


def test_get_user_by_id_failed(user_repository, app):
    with app.app_context():
        retrieved_user = user_repository.get_user_by_id(99999)
        assert retrieved_user is None


def test_get_user_by_email_success(user_repository, app):
    with app.app_context():
        retrieved_user = user_repository.get_user_by_email("success.email@email.com")
        assert retrieved_user is not None
        assert retrieved_user.name == "Success User"


def test_get_user_by_email_failed(user_repository, app):
    with app.app_context():
        retrieved_user = user_repository.get_user_by_email("nonexistent.email@email.com")
        assert retrieved_user is None
