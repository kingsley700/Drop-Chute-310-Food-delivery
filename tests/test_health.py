from fastapi.testclient import TestClient
from app.main import app
from app.schemas.health import HealthResponse

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}
    HealthResponse(**response.json())


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Food Delivery Api is running"}


def test_docs():
    assert client.get("/docs").status_code == 200


def test_unknown_path():
    assert client.get("/does-not-exist").status_code == 404
