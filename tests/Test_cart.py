
from app.repositories import cart_repo


def test_create_cart(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")

    monkeypatch.setattr(cart_repo, "filep", str(file))

    cart = cart_repo.create_cart(1)

    assert cart.id == 1
    assert cart.customer_id == 1
    assert cart.status == "active"


def test_get_cart_by_customer(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")

    monkeypatch.setattr(cart_repo, "filep", str(file))

    cart_repo.create_cart(1)

    cart = cart_repo.get_cart_by_customer(1)

    assert cart is not None
    assert cart.customer_id == 1


def test_customer_without_cart(tmp_path, monkeypatch):
    file = tmp_path / "carts.json"
    file.write_text("[]")

    monkeypatch.setattr(cart_repo, "filep", str(file))

    cart = cart_repo.get_cart_by_customer(1)

    assert cart is None
