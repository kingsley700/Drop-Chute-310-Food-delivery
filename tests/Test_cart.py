from fastapi import HTTPException
from app.repositories import cart_repo, customer_repository
from app.services import cart_service


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


def test_get_cart_by_customer(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)

    cart_repo.create_cart(1)
    cart = cart_repo.get_cart_by_customer(1)

    assert cart is not None
    assert cart.customer_id == 1


def test_customer_without_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)

    cart = cart_repo.get_cart_by_customer(1)

    assert cart is None


def test_service_creates_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)
    monkeypatch.setattr(customer_repository,"get_customer_by_id",lambda customer_id: type("Customer", (), {"is_active": True})())

    cart = cart_service.get_or_create_cart(1)

    assert cart.customer_id == 1
    assert cart.status == "active"


def test_service_returns_existing_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)
    monkeypatch.setattr(customer_repository,"get_customer_by_id",lambda customer_id: type("Customer", (), {"is_active": True})())

    first_cart = cart_service.get_or_create_cart(1)
    second_cart = cart_service.get_or_create_cart(1)

    assert first_cart.id == second_cart.id


def test_service_rejects_missing_customer(monkeypatch):
    monkeypatch.setattr(customer_repository, "get_customer_by_id", lambda customer_id: None)

    try:
        cart_service.get_or_create_cart(1)
        assert False
    except HTTPException as error:
        assert error.status_code == 404


def test_deactivated_customer_cannot_access_cart(tmp_path, monkeypatch):
    setup_cart_file(tmp_path, monkeypatch)
    cart_repo.create_cart(1)

    monkeypatch.setattr(customer_repository,"get_customer_by_id",lambda customer_id: type("Customer", (), {"is_active": False})())

    try:
        cart_service.get_or_create_cart(1)
        assert False
    except HTTPException as error:
        assert error.status_code == 403