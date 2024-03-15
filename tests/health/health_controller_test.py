import pytest

from src import create_app


@pytest.fixture
def app():
    app = create_app()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(client):
    response = client.get('/api/healthcheck')
    data = response.get_json()

    assert response.status_code == 200
    assert data['status'] == 'OK'
    assert data['message'] == 'Service is up and running.'
