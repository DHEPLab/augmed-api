def test_health_check(client):
    response = client.get("/api/healthcheck")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "OK"
    assert data["message"] == "Service is up and running."
