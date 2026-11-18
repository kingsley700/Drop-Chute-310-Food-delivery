import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.repositories import cart_repo, customer_repository
from app.services import cart_service, restaurant_services
from app.main import app

client = TestClient(app)


def setup_cart_file(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")
    monkeypatch.setattr(cart_repo, "filep", str(file))


def setup_add_item(tmp_path, monkeypatch, active=True):
    setup_cart_file(tmp_path, monkeypatch)
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: type("Customer", (), {"is_active": active})())

    restaurants = {
        1: {
            "id": 1,
            "items": [
                {"name": "Burger", "price": 10.0, "available": True},
                {"name": "Pizza", "price": 12.0, "available": False}
            ]
        },
        2: {
            "id": 2,
            "items": [
                {"name": "Pasta", "price": 15.0, "available": True}
            ]
        }
    }

    monkeypatch.setattr(restaurant_services, "get_restaurant_by_id", lambda restaurant_id: restaurants.get(restaurant_id))


def test_create_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)

    cart = cart_repo.create_cart(1)

    assert cart.id == 1
    assert cart.customer_id == 1
    assert cart.status == "active"


def test_service_get_or_create_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: type("Customer", (), {"is_active": True})())

    first_cart = cart_service.get_or_create_cart(1)
    second_cart = cart_service.get_or_create_cart(1)

    assert first_cart.id == second_cart.id
    assert second_cart.status == "active"


def test_service_rejects_deactivated_customer(monkeypatch):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: type("Customer", (), {"is_active": False})())

    with pytest.raises(HTTPException) as error:
        cart_service.get_or_create_cart(1)

    assert error.value.status_code == 403


def test_cart_endpoints(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: type("Customer", (), {"is_active": True})())

    get_response = client.get("/customers/1/cart")
    post_response = client.post("/customers/1/cart")

    assert get_response.status_code == 200
    assert post_response.status_code == 200
    assert get_response.json()["id"] == post_response.json()["id"]


def test_cart_endpoint_rejects_missing_customer(monkeypatch):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: None)

    response = client.get("/customers/1/cart")

    assert response.status_code == 404


def test_add_item_to_cart(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch)

    response = client.post("/customers/1/cart/items", json={
        "restaurant_id": 1,
        "item_name": "Burger",
        "quantity": 2
    })

    assert response.status_code == 200
    assert response.json()["restaurant_id"] == 1
    assert response.json()["items"][0]["name"] == "Burger"
    assert response.json()["items"][0]["quantity"] == 2


@pytest.mark.parametrize("item_name, quantity, status_code", [
    ("Salad", 1, 404),
    ("Pizza", 1, 400),
    ("Burger", 0, 422),
    ("Burger", -1, 422)
])
def test_add_item_rejects_invalid_items(tmp_path, monkeypatch, item_name, quantity, status_code):
    setup_add_item(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as error:
        cart_service.add_item_to_cart(1, 1, item_name, quantity)

    assert error.value.status_code == status_code


def test_add_item_rejects_different_restaurant(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch)

    cart_service.add_item_to_cart(1, 1, "Burger", 1)

    with pytest.raises(HTTPException) as error:
        cart_service.add_item_to_cart(1, 2, "Pasta", 1)

    assert error.value.status_code == 400


def test_deactivated_customer_cannot_add_item(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch, active=False)

    with pytest.raises(HTTPException) as error:
        cart_service.add_item_to_cart(1, 1, "Burger", 1)

    assert error.value.status_code == 403


def test_update_cart_item_quantity(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch)

    cart_service.add_item_to_cart(1, 1, "Burger", 2)

    response = client.patch("/customers/1/cart/items/Burger", json={
        "quantity": 3
    })

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3


def test_update_missing_cart_item(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch)

    cart_service.get_or_create_cart(1)

    response = client.patch("/customers/1/cart/items/Burger", json={
        "quantity": 2
    })

    assert response.status_code == 404


@pytest.mark.parametrize("quantity", [0, -1])
def test_update_invalid_quantity(tmp_path, monkeypatch, quantity):
    setup_add_item(tmp_path, monkeypatch)

    cart_service.add_item_to_cart(1, 1, "Burger", 2)

    response = client.patch("/customers/1/cart/items/Burger", json={
        "quantity": quantity
    })

    assert response.status_code == 422


def test_update_cart_recalculates_totals(tmp_path, monkeypatch):
    setup_add_item(tmp_path, monkeypatch)

    cart_service.add_item_to_cart(1, 1, "Burger", 2)

    response = client.patch("/customers/1/cart/items/Burger", json={
        "quantity": 3
    })

    assert response.status_code == 200
    assert response.json()["subtotal"] == 30.0
    assert response.json()["tax"] == 3.6
    assert response.json()["total"] == 33.6
