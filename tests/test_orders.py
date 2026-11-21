import json
import pytest
from uuid import uuid4
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.cart import Cart, CartItem
from app.repositories import order_repo, cart_repo, customer_repository
from app.services import checkout_service, cart_service, restaurant_services, order_service


client = TestClient(app)


# Setup
@pytest.fixture
def setup(tmp_path, monkeypatch):
    orders = tmp_path / "orders.json"
    carts = tmp_path / "carts.json"
    orders.write_text("[]")
    carts.write_text("[]")

    monkeypatch.setattr(order_repo, "filep", str(orders))
    monkeypatch.setattr(cart_repo, "filep", str(carts))
    monkeypatch.setattr(customer_repository, "get_customer_by_id",
                        lambda id: SimpleNamespace(id=id, is_active=True))
    monkeypatch.setattr(restaurant_services, "get_restaurant_by_id",
                        lambda id: {"items": [{"name": "Burger", "price": 10.0, "available": True}]})

    return orders



def test_create_order(setup, monkeypatch):
    cart = Cart(
        id=1, customer_id=1, restaurant_id=uuid4(),
        items=[CartItem(name="Burger", price=10, quantity=2)],
        subtotal=20, tax=2.4, total=22.4
    )

    monkeypatch.setattr(checkout_service, "validate_checkout", lambda id: cart)
    monkeypatch.setattr(checkout_service, "validate_menu_items", lambda cart: cart)
    monkeypatch.setattr(cart_service, "clear_cart", lambda id: None)

    response = client.post("/customers/1/orders")

    assert response.status_code == 200
    assert response.json()["customer_id"] == 1
    assert response.json()["total"] == 22.4

    saved = json.loads(setup.read_text())
    assert len(saved) == 1
    assert saved[0]["items"][0]["name"] == "Burger"


def test_create_order_invalid_checkout(setup, monkeypatch):
    monkeypatch.setattr(checkout_service, "validate_checkout",
                        lambda id: (_ for _ in ()).throw(HTTPException(400, "Cart is empty")))

    response = client.post("/customers/1/orders")

    assert response.status_code == 400
    assert json.loads(setup.read_text()) == []


# Cart clearing tests
def test_successful_order_clears_cart(setup):
    cart_service.add_item_to_cart(1, uuid4(), "Burger", 2)

    response = client.post("/customers/1/orders")

    assert response.status_code == 200
    assert cart_service.get_cart(1).items == []


def test_failed_order_preserves_cart(setup, monkeypatch):
    cart_service.add_item_to_cart(1, uuid4(), "Burger", 2)
    monkeypatch.setattr(order_repo, "create_order",
                        lambda order: (_ for _ in ()).throw(Exception("Save failed")))

    with pytest.raises(Exception):
        order_service.create_order(1)

    cart = cart_service.get_cart(1)
    assert cart.items[0].name == "Burger"
    assert cart.items[0].quantity == 2
    assert cart.total == 22.4


def test_failed_checkout_preserves_cart(setup, monkeypatch):
    cart_service.add_item_to_cart(1, uuid4(), "Burger", 2)
    monkeypatch.setattr(checkout_service, "validate_checkout",
                        lambda id: (_ for _ in ()).throw(HTTPException(400, "Checkout failed")))

    response = client.post("/customers/1/orders")

    assert response.status_code == 400
    cart = cart_service.get_cart(1)
    assert cart.items[0].name == "Burger"
    assert cart.items[0].quantity == 2
