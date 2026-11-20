import pytest
from uuid import UUID
from types import SimpleNamespace
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import cart_repo, customer_repository
from app.services import cart_service, checkout_service, restaurant_services

RESTAURANT_ID = UUID("b6a58c65-6e0f-4d3d-af12-f95af139573a")
client = TestClient(app)


# Setup
@pytest.fixture
def setup(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")
    monkeypatch.setattr(cart_repo, "filep", str(file))
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda id: SimpleNamespace(id=id, is_active=True))
    monkeypatch.setattr(restaurant_services, "get_restaurant_by_id", lambda id: {
        "items": [{"name": "Burger", "price": 15.0, "active": True, "available": True}]
    })


# Service tests
def test_validate_checkout(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    assert checkout_service.validate_checkout(1).items[0].name == "Burger"


def test_invalid_customer(setup, monkeypatch):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda id: None)
    with pytest.raises(HTTPException) as e:
        checkout_service.validate_checkout(1)
    assert e.value.status_code == 404


def test_empty_cart(setup):
    cart_service.get_or_create_cart(1)
    with pytest.raises(HTTPException) as e:
        checkout_service.validate_checkout(1)
    assert e.value.status_code == 400


def test_price_recalculation(setup, monkeypatch):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    cart = cart_repo.get_cart_by_customer(1)
    monkeypatch.setattr(restaurant_services, "get_restaurant_by_id", lambda id: {
        "items": [{"name": "Burger", "price": 20.0, "active": True, "available": True}]
    })

    result = checkout_service.validate_menu_items(cart)
    assert result.subtotal == 40.0
    assert result.tax == 4.8
    assert result.total == 44.8


# API test
def test_checkout_endpoint(setup):
    cart_service.add_item_to_cart(1, RESTAURANT_ID, "Burger", 2)
    response = client.post("/customers/1/checkout/validate")
    assert response.status_code == 200