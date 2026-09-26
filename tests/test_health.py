from fastapi.testclient import TestClient
from app.main import app

# Use python -m pytest -v when testing. NOT pytest -v

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}
