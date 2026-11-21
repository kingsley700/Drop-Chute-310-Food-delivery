import json
import pytest
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.cart import Cart, CartItem
from app.repositories import order_repo
from app.services import checkout_service


client = TestClient(app)


@pytest.fixture
def orders_file(tmp_path, monkeypatch):
    file = tmp_path / "orders.json"
    file.write_text("[]")
    monkeypatch.setattr(order_repo, "filep", str(file))
    return file



def test_create_order(orders_file, monkeypatch):
    cart = Cart(
        id=1,
        customer_id=1,
        restaurant_id=uuid4(),
        items=[CartItem(name="Burger", price=10, quantity=2)],
        subtotal=20,
        tax=2.4,
        total=22.4
    )

    monkeypatch.setattr(checkout_service, "validate_checkout", lambda customer_id: cart)
    monkeypatch.setattr(checkout_service, "validate_menu_items", lambda cart: cart)

    response = client.post("/customers/1/orders")

    assert response.status_code == 200
    assert response.json()["customer_id"] == 1
    assert response.json()["total"] == 22.4

    saved_orders = json.loads(orders_file.read_text())
    assert len(saved_orders) == 1
    assert saved_orders[0]["items"][0]["name"] == "Burger"



def test_create_order_invalid_checkout(orders_file, monkeypatch):
    def invalid_checkout(customer_id):
        raise HTTPException(400, "Cart is empty")

    monkeypatch.setattr(checkout_service, "validate_checkout", invalid_checkout)

    response = client.post("/customers/1/orders")

    assert response.status_code == 400
    assert json.loads(orders_file.read_text()) == []
