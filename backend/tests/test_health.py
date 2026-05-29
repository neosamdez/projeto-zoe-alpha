def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Amenti Core Online"


def test_openapi_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_unauthorized_access(client):
    response = client.get("/api/v1/leads/")
    assert response.status_code == 401
