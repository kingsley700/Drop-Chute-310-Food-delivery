from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import restaurants as rest_route

client = TestClient(app)

def test_restaurant_list():
    response = client.get("/restaurants")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "cuisine" in first
    assert "items" in first
    

def test_restaurant_empty_data(monkeypatch):
    monkeypatch.setattr(rest_route, "get_restaurants", lambda: [])
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert response.json() == []
    

def test_restaurant_list_wrong_method():
    response = client.post("/restaurants", json={})
    assert response.status_code == 405