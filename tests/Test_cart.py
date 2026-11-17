from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.repositories import cart_repo, customer_repository
from app.services import cart_service
from app.main import app

client = TestClient(app)


def setup_cart_file(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")
    monkeypatch.setattr(cart_repo, "filep", str(file))


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

    try:
        cart_service.get_or_create_cart(1)
        assert False
    except HTTPException as error:
        assert error.status_code == 403


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