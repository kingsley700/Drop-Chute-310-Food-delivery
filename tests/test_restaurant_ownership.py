import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import customer_repository, restaurant_repository
from app.tokens import create_access_token

client = TestClient(app)

SAMS_RESTAURANT = "11111111-1111-4111-8111-111111111111"


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    customers = tmp_path / "customers.json"
    customers.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(customers))

    restaurants = tmp_path / "restaurants.json"
    restaurants.write_text(
        json.dumps([{"id": SAMS_RESTAURANT, "name": "Pizza Place", "cuisine": "Italian", "items": [], "owner_id": 1}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(restaurant_repository, "filep", str(restaurants))

    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    customer_repository.create_customer("Sam Graham", "sam@gmail.com", "hash1", "755 Academy Way")
    customer_repository.create_customer("Alex Roy", "alex@gmail.com", "hash2", "12 Main Street")


def auth(customer_id):
    return {"Authorization": "Bearer " + create_access_token(customer_id)}


def test_create_restaurant_needs_sign_in():
    response = client.post("/CreateRestaurant", json={"name": "Sushi Spot", "cuisine": "Japanese"})

    assert response.status_code == 401


def test_created_restaurant_belongs_to_creator():
    created = client.post("/CreateRestaurant", json={"name": "Sushi Spot", "cuisine": "Japanese"}, headers=auth(2))
    assert created.status_code == 201

    mine = client.get("/restaurants/mine", headers=auth(2)).json()
    assert [r["name"] for r in mine] == ["Sushi Spot"]
    assert client.get("/restaurants/mine", headers=auth(1)).json()[0]["name"] == "Pizza Place"


def test_owner_can_update_own_restaurant():
    response = client.patch(f"/restaurants/{SAMS_RESTAURANT}", json={"name": "Pizza Palace"}, headers=auth(1))

    assert response.status_code == 200
    assert response.json()["name"] == "Pizza Palace"


def test_update_without_token_returns_401():
    response = client.patch(f"/restaurants/{SAMS_RESTAURANT}", json={"name": "Hacked"})

    assert response.status_code == 401


def test_update_someone_elses_restaurant_returns_403():
    response = client.patch(f"/restaurants/{SAMS_RESTAURANT}", json={"name": "Hacked"}, headers=auth(2))

    assert response.status_code == 403
    assert restaurant_repository.get_restaurant_by_id(SAMS_RESTAURANT)["name"] == "Pizza Place"


def test_update_nonexistent_restaurant_returns_404():
    response = client.patch("/restaurants/22222222-2222-4222-8222-222222222222", json={"name": "X"}, headers=auth(1))

    assert response.status_code == 404