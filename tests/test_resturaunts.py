import json
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import restaurant_repository as repo
from app.services import restaurant_services as service
from app.schemas.restaurantschemas import Restaurant, RestaurantCreate, RestaurantItem

GOLDEN_ISLAND_ID = UUID("b6a58c65-6e0f-4d3d-af12-f95af139573a")
BAMBOO_CHOPSTICKS_ID = UUID("6fea0a67-0de0-4513-8ee3-eb10ed2535f1")
CHIPOTLE_ID = UUID("571a0f53-f2bf-43f9-8c60-2a8d369301ea")
UNKNOWN_ID = UUID("247d66a6-1b4d-46d5-9a34-2257c5ab1ca2")

client = TestClient(app)


@pytest.fixture
def restaurant_file(tmp_path, monkeypatch):
    data = [
        {"id": str(GOLDEN_ISLAND_ID), "name": "Golden Island", "cuisine": "Chinese", "items": [
            {"name": "Can Pop", "price": 2.25, "available": True}
        ]},
        {"id": str(BAMBOO_CHOPSTICKS_ID), "name": "Bamboo Chopsticks", "cuisine": "Vietnamese", "items": []},
        {"id": str(CHIPOTLE_ID), "name": "Chipotle", "cuisine": "Mexican", "items": []}
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
    assert [r["id"] for r in response.json()] == [str(GOLDEN_ISLAND_ID), str(BAMBOO_CHOPSTICKS_ID), str(CHIPOTLE_ID)]
    for restaurant in response.json():
        Restaurant(**restaurant)


def test_empty_restaurants(restaurant_file):
    restaurant_file.write_text("[]")
    assert client.get("/restaurants").json() == []


def test_create_restaurant(restaurant_file):
    response = client.post("/CreateRestaurant", json={
        "name": "Tossings", "cuisine": "Italian"
    })
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Tossings"
    assert str(UUID(created["id"])) == created["id"]
    assert created["items"] == []


def test_create_invalid_restaurant(restaurant_file):
    assert client.post("/CreateRestaurant", json={"name": "Tossings"}).status_code == 422


def test_add_item(restaurant_file):
    response = client.post(f"/restaurants/{CHIPOTLE_ID}/items", json={"name": "Burrito", "price": 12})
    assert response.status_code == 201
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"


def test_malformed_restaurant_id(restaurant_file):
    assert client.patch("/restaurants/invalid", json={"name": "Unknown"}).status_code == 422


def test_add_item_unknown_restaurant(restaurant_file):
    assert client.post(f"/restaurants/{UNKNOWN_ID}/items", json={"name": "Burrito", "price": 12}).status_code == 404


def test_update_restaurant(restaurant_file):
    response = client.patch(f"/restaurants/{GOLDEN_ISLAND_ID}", json={"name": "New Name", "cuisine": "Japanese"})
    assert response.status_code == 200
    assert read_file(restaurant_file)[0]["name"] == "New Name"


def test_update_unknown_restaurant(restaurant_file):
    assert client.patch(f"/restaurants/{UNKNOWN_ID}", json={"name": "Unknown"}).status_code == 404


def test_update_item(restaurant_file):
    response = client.patch(f"/restaurants/{GOLDEN_ISLAND_ID}/items/Can Pop", json={"name": "Soda", "price": 3})
    assert response.status_code == 200
    assert read_file(restaurant_file)[0]["items"][0]["name"] == "Soda"


@pytest.mark.parametrize("restaurant_id,item,status", [
    (GOLDEN_ISLAND_ID, "Donut", 404),
    (UNKNOWN_ID, "Can Pop", 404)
])
def test_update_item_unknown(restaurant_file, restaurant_id, item, status):
    response = client.patch(f"/restaurants/{restaurant_id}/items/{item}", json={"price": 3})
    assert response.status_code == status


def test_invalid_price(restaurant_file):
    assert client.patch(f"/restaurants/{GOLDEN_ISLAND_ID}/items/Can Pop", json={"price": -1}).status_code == 422


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
    assert repo.get_restaurant_by_id(BAMBOO_CHOPSTICKS_ID)["name"] == "Bamboo Chopsticks"
    assert repo.get_restaurant_by_id(UNKNOWN_ID) is None


def test_create_restaurant_repository(restaurant_file):
    created = repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
    assert str(UUID(created["id"])) == created["id"]
    assert read_file(restaurant_file)[-1]["name"] == "Tossings"


def test_update_restaurant_repository(restaurant_file):
    repo.update_restaurant_name(GOLDEN_ISLAND_ID, "New Name")
    repo.update_restaurant_cuisine(GOLDEN_ISLAND_ID, "Japanese")
    data = read_file(restaurant_file)[0]
    assert data["name"] == "New Name"
    assert data["cuisine"] == "Japanese"


def test_delete_restaurant_repository(restaurant_file):
    assert repo.delete_restaurant(BAMBOO_CHOPSTICKS_ID) is True
    assert len(repo.get_restaurants()) == 2
    assert repo.delete_restaurant(UNKNOWN_ID) is False


def test_add_item_repository(restaurant_file):
    repo.add_restaurant_items(CHIPOTLE_ID, {"name": "Burrito", "price": 12})
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"
    assert repo.add_restaurant_items(UNKNOWN_ID, {"name": "X", "price": 1}) is None


def test_update_item_repository(restaurant_file):
    repo.update_restaurant_item(GOLDEN_ISLAND_ID, "Can Pop", new_name="Soda", price=3, available=False)
    item = read_file(restaurant_file)[0]["items"][0]
    assert item["name"] == "Soda"
    assert item["available"] is False
    assert repo.update_restaurant_item(GOLDEN_ISLAND_ID, "Donut", price=1) is None


def test_delete_item_repository(restaurant_file):
    repo.delete_restaurant_item(GOLDEN_ISLAND_ID, "Can Pop")
    assert read_file(restaurant_file)[0]["items"] == []



# Service tests

def test_get_restaurants_service(restaurant_file):
    assert len(service.get_restaurants()) == 3
    assert service.get_restaurant_by_id(BAMBOO_CHOPSTICKS_ID)["name"] == "Bamboo Chopsticks"
    assert service.get_restaurant_by_name("Bamboo Chopsticks")["cuisine"] == "Vietnamese"


def test_create_restaurant_service(restaurant_file):
    restaurant = RestaurantCreate(name="Tossings", cuisine="Italian")
    created = service.create_restaurant(restaurant)
    assert str(UUID(created["id"])) == created["id"]


def test_update_restaurant_service(restaurant_file):
    service.update_restaurant_name(GOLDEN_ISLAND_ID, "New Name")
    service.update_restaurant_cuisine(GOLDEN_ISLAND_ID, "Japanese")
    assert service.get_restaurant_by_id(GOLDEN_ISLAND_ID)["name"] == "New Name"
    assert service.get_restaurant_by_id(GOLDEN_ISLAND_ID)["cuisine"] == "Japanese"


def test_delete_restaurant_service(restaurant_file):
    assert service.delete_restaurant(BAMBOO_CHOPSTICKS_ID) is True
    assert service.delete_restaurant(UNKNOWN_ID) is False


def test_add_item_service(restaurant_file):
    item = RestaurantItem(name="Burrito", price=12)
    service.add_restaurant_items(CHIPOTLE_ID, item)
    assert read_file(restaurant_file)[2]["items"][0]["name"] == "Burrito"
    with pytest.raises(ValueError):
        service.add_restaurant_items(UNKNOWN_ID, item)


def test_update_item_service(restaurant_file):
    service.update_restaurant_item(GOLDEN_ISLAND_ID, "Can Pop", new_name="Soda", price=3, available=False)
    item = read_file(restaurant_file)[0]["items"][0]
    assert item["name"] == "Soda"
    assert item["available"] is False
    with pytest.raises(ValueError):
        service.update_restaurant_item(GOLDEN_ISLAND_ID, "Donut", price=1)


def test_delete_item_service(restaurant_file):
    service.delete_restaurant_item(GOLDEN_ISLAND_ID, "Can Pop")
    assert read_file(restaurant_file)[0]["items"] == []
