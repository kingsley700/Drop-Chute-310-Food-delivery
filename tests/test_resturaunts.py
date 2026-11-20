
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import restaurant_repository as repo
from app.services import restaurant_services as service
from app.schemas.restaurantschemas import Restaurant, RestaurantItem

client = TestClient(app)


@pytest.fixture
def restaurant_file(tmp_path, monkeypatch):
    data = [
        {"id": 1, "name": "Golden Island", "cuisine": "Chinese", "items": [
            {"name": "Can Pop", "price": 2.25, "available": True}
        ]},
        {"id": 2, "name": "Bamboo Chopsticks", "cuisine": "Vietnamese", "items": []},
        {"id": 3, "name": "Chipotle", "cuisine": "Mexican", "items": []}
    ]
    file = tmp_path / "restaurants.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(repo, "filep", str(file))
    return file


def read_file(file):
    return json.loads(file.read_text(encoding="utf-8"))


# API tests

def test_list_restaurants(restaurant_file):
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [1, 2, 3]
    for restaurant in response.json():
        Restaurant(**restaurant)


def test_empty_restaurants(restaurant_file):
    restaurant_file.write_text("[]")
    assert client.get("/restaurants").json() == []


def test_create_restaurant(restaurant_file):
    response = client.post("/CreateRestaurant", json={
        "id": 0, "name": "Tossings", "cuisine": "Italian", "items": []
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Tossings"


def test_create_invalid_restaurant(restaurant_file):
    assert client.post("/CreateRestaurant", json={"name": "Tossings"}).status_code == 422


def test_add_item(restaurant_file):
    response = client.post("/restaurants/3/items", json={"name": "Burrito", "price": 12})
    assert response.status_code == 201
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"


def test_add_item_unknown_restaurant(restaurant_file):
    assert client.post("/restaurants/999/items", json={"name": "Burrito", "price": 12}).status_code == 404


def test_update_restaurant(restaurant_file):
    response = client.patch("/restaurants/1", json={"name": "New Name", "cuisine": "Japanese"})
    assert response.status_code == 200
    assert read_file(restaurant_file)[0]["name"] == "New Name"


def test_update_unknown_restaurant(restaurant_file):
    assert client.patch("/restaurants/999", json={"name": "Unknown"}).status_code == 404


def test_update_item(restaurant_file):
    response = client.patch("/restaurants/1/items/Can Pop", json={"name": "Soda", "price": 3})
    assert response.status_code == 200
    assert read_file(restaurant_file)[0]["items"][0]["name"] == "Soda"


@pytest.mark.parametrize("restaurant_id,item,status", [
    (1, "Donut", 404),
    (999, "Can Pop", 404)
])
def test_update_item_unknown(restaurant_file, restaurant_id, item, status):
    response = client.patch(f"/restaurants/{restaurant_id}/items/{item}", json={"price": 3})
    assert response.status_code == status


def test_invalid_price(restaurant_file):
    assert client.patch("/restaurants/1/items/Can Pop", json={"price": -1}).status_code == 422


def test_wrong_methods(restaurant_file):
    assert client.post("/restaurants").status_code == 405
    assert client.delete("/restaurants").status_code == 405


def test_missing_file(restaurant_file):
    restaurant_file.unlink()
    response = TestClient(app, raise_server_exceptions=False).get("/restaurants")
    assert response.status_code == 500


def test_corrupt_file(restaurant_file):
    restaurant_file.write_text("{invalid json")
    with pytest.raises(json.JSONDecodeError):
        repo.get_restaurants()


# Repository tests

def test_get_restaurants(restaurant_file):
    assert len(repo.get_restaurants()) == 3
    assert repo.get_restaurant_by_id(2)["name"] == "Bamboo Chopsticks"
    assert repo.get_restaurant_by_id(999) is None


def test_create_restaurant_repository(restaurant_file):
    created = repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
    assert created["id"] == 4
    assert read_file(restaurant_file)[-1]["name"] == "Tossings"


def test_update_restaurant_repository(restaurant_file):
    repo.update_restaurant_name(1, "New Name")
    repo.update_restaurant_cuisine(1, "Japanese")
    data = read_file(restaurant_file)[0]
    assert data["name"] == "New Name"
    assert data["cuisine"] == "Japanese"


def test_delete_restaurant_repository(restaurant_file):
    assert repo.delete_restaurant(2) is True
    assert len(repo.get_restaurants()) == 2
    assert repo.delete_restaurant(999) is False


def test_add_item_repository(restaurant_file):
    repo.add_restaurant_items(3, {"name": "Burrito", "price": 12})
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"
    assert repo.add_restaurant_items(999, {"name": "X", "price": 1}) is None


def test_update_item_repository(restaurant_file):
    repo.update_restaurant_item(1, "Can Pop", new_name="Soda", price=3, available=False)
    item = read_file(restaurant_file)[0]["items"][0]
    assert item["name"] == "Soda"
    assert item["available"] is False
    assert repo.update_restaurant_item(1, "Donut", price=1) is None


def test_delete_item_repository(restaurant_file):
    repo.delete_restaurant_item(1, "Can Pop")
    assert read_file(restaurant_file)[0]["items"] == []


def test_swap_ids_repository(restaurant_file):
    repo.swap_restaurant_id(1, 3)
    assert repo.get_restaurant_by_id(1)["name"] == "Chipotle"
    assert repo.swap_restaurant_id(1, 999) is None


# Service tests

def test_get_restaurants_service(restaurant_file):
    assert len(service.get_restaurants()) == 3
    assert service.get_restaurant_by_id(2)["name"] == "Bamboo Chopsticks"
    assert service.get_restaurant_by_name("Bamboo Chopsticks")["cuisine"] == "Vietnamese"


def test_create_restaurant_service(restaurant_file):
    restaurant = Restaurant(id=0, name="Tossings", cuisine="Italian", items=[])
    assert service.create_restaurant(restaurant)["id"] == 4


def test_update_restaurant_service(restaurant_file):
    service.update_restaurant_name(1, "New Name")
    service.update_restaurant_cuisine(1, "Japanese")
    assert service.get_restaurant_by_id(1)["name"] == "New Name"
    assert service.get_restaurant_by_id(1)["cuisine"] == "Japanese"


def test_delete_restaurant_service(restaurant_file):
    assert service.delete_restaurant(2) is True
    assert service.delete_restaurant(999) is False


def test_add_item_service(restaurant_file):
    item = RestaurantItem(name="Burrito", price=12)
    service.add_restaurant_items(3, item)
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"
    assert service.add_restaurant_items(999, item) is None


def test_update_item_service(restaurant_file):
    service.update_restaurant_item(1, "Can Pop", new_name="Soda", price=3, available=False)
    item = read_file(restaurant_file)[0]["items"][0]
    assert item["name"] == "Soda"
    assert item["available"] is False
    assert service.update_restaurant_item(1, "Donut", price=1) is None


def test_delete_item_service(restaurant_file):
    service.delete_restaurant_item(1, "Can Pop")
    assert read_file(restaurant_file)[0]["items"] == []


def test_swap_ids_service(restaurant_file):
    service.swap_restaurant_id(1, 3)
    assert service.get_restaurant_by_id(1)["name"] == "Chipotle"
