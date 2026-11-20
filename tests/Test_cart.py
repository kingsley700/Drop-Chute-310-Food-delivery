
import pytest
from uuid import UUID
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.repositories import cart_repo, customer_repository
from app.services import cart_service, restaurant_services
from app.main import app

RESTAURANT_ID = UUID("b6a58c65-6e0f-4d3d-af12-f95af139573a")
OTHER_RESTAURANT_ID = UUID("6fea0a67-0de0-4513-8ee3-eb10ed2535f1")

client = TestClient(app)


# Sets up test data
@pytest.fixture
def setup(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")
    monkeypatch.setattr(cart_repo, "filep", str(file))
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda id: SimpleNamespace(id=id, is_active=True))
    monkeypatch.setattr(restaurant_services, "get_restaurant_by_id", lambda id: {
        "id": id,
        "items": [
            {"name": "Burger", "price": 10.0, "available": True},
            {"name": "Pizza", "price": 12.0, "available": False}
        ]
    })


# Checks cart data
def check_cart(data, **expected):
    for key, value in expected.items():
        if value is not None:
            assert data[key] == value


# Checks item data
def check_item(data, **expected):
    for key, value in expected.items():
        if value is not None:
            assert data["items"][0][key] == value


# Repository tests
def test_create_cart(setup):
    cart = cart_repo.create_cart(1)
    check_cart(cart.model_dump(), customer_id=1, status="active")


# Service tests
def test_service_get_or_create_cart(setup):
    cart1 = cart_service.get_or_create_cart(1)
    cart2 = cart_service.get_or_create_cart(1)
    assert cart1.id == cart2.id


@pytest.mark.parametrize("item,quantity,status", [
    ("Salad", 1, 404),
    ("Pizza", 1, 400),
    ("Burger", 0, 422),
    ("Burger", -1, 422)
])
def test_add_item_rejects_invalid_items(setup, item, quantity, status):
    with pytest.raises(HTTPException) as e:
        cart_service.add_item_to_cart(1, RESTAURANT_ID, item, quantity)
    assert e.value.status_code == status


def test_add_item_rejects_different_restaurant(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 1)
    with pytest.raises(HTTPException) as e:
        cart_service.add_item_to_cart(1, OTHER_RESTAURANT_ID, "Burger", 1)
    assert e.value.status_code == 400


@pytest.mark.parametrize("action,args", [
    (cart_service.get_or_create_cart, (1,)),
    (cart_service.add_item_to_cart, (1, RESTAURANT_ID, "Burger", 1)),
    (cart_service.clear_cart, (1,)),
    (cart_service.get_cart, (1,))
])
def test_deactivated_customer_rejected(setup, monkeypatch, action, args):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda id: SimpleNamespace(id=id, is_active=False))
    with pytest.raises(HTTPException) as e:
        action(*args)
    assert e.value.status_code == 403


# API tests
def test_cart_endpoint_rejects_missing_customer(setup, monkeypatch):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda id: None)
    response = client.get("/customers/999/cart")
    assert response.status_code == 404


def test_add_item_to_cart(setup):
    response = client.post("/customers/1/cart/items", json={"restaurant_id": str(RESTAURANT_ID), "item_name": "Burger", "quantity": 2})
    assert response.status_code == 200
    check_cart(response.json(), customer_id=1, restaurant_id=str(RESTAURANT_ID), subtotal=20.0, tax=2.4, total=22.4)
    check_item(response.json(), name="Burger", price=10.0, quantity=2)


def test_update_cart_item_quantity(setup):
    client.post("/customers/1/cart/items", json={"restaurant_id": str(RESTAURANT_ID), "item_name": "Burger", "quantity": 1})
    response = client.patch("/customers/1/cart/items/Burger", json={"quantity": 3})
    assert response.status_code == 200
    check_item(response.json(), quantity=3)


@pytest.mark.parametrize("quantity", [0, -1])
def test_update_invalid_quantity(setup, quantity):
    with pytest.raises(HTTPException) as e:
        cart_service.update_cart_item_quantity(1, "Burger", quantity)
    assert e.value.status_code == 422


def test_update_cart_recalculates_totals(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 1)
    response = client.patch("/customers/1/cart/items/Burger", json={"quantity": 3})
    assert response.status_code == 200
    check_cart(response.json(), subtotal=30.0, tax=3.6, total=33.6)


def test_remove_cart_item(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    data = client.delete("/customers/1/cart/items/Burger").json()
    assert data["items"] == []
    check_cart(data, subtotal=0, tax=0, total=0)


def test_remove_missing_cart_item(setup):
    with pytest.raises(HTTPException) as e:
        cart_service.remove_cart_item(1, "Burger")
    assert e.value.status_code == 404


def test_clear_cart(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    data = client.delete("/customers/1/cart").json()
    assert data["items"] == []
    assert data["status"] == "active"
    check_cart(data, subtotal=0, tax=0, total=0)


def test_get_cart_contents(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    response = client.get("/customers/1/cart")
    assert response.status_code == 200
    check_cart(response.json(), customer_id=1, restaurant_id=str(RESTAURANT_ID), subtotal=20.0, tax=2.4, total=22.4)
    check_item(response.json(), name="Burger", price=10.0, quantity=2)


def test_get_cart_not_found(setup):
    with pytest.raises(HTTPException) as e:
        cart_service.get_cart(2)
    assert e.value.status_code == 404
