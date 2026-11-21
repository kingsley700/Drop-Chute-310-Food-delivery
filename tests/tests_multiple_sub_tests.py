import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import cart_repo, customer_repository, order_repo, restaurant_repository
from app.security import hash_password
from app.tokens import create_access_token

client = TestClient(app)


#vassili






#teppei





#rayan

@pytest.fixture
def order_flow_files(tmp_path, monkeypatch):
    """Real repositories pointed at temporary files, with one restaurant and its menu. Nothing is mocked."""
    for repo, name in [(customer_repository, "customers"), (restaurant_repository, "restaurants"), (cart_repo, "carts"), (order_repo, "orders")]:
        file = tmp_path / f"{name}.json"
        file.write_text("[]")
        monkeypatch.setattr(repo, "filep", str(file))
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    restaurant_repository.create_restaurant({
        "name": "Golden Island",
        "cuisine": "Chinese",
        "items": [
            {"name": "Burger", "price": 10.0, "available": True},
            {"name": "Fries", "price": 4.0, "available": True},
        ],
    })


# Registers and signs in through the API, then follows the menu into a cart, checkout and a saved order
def test_customer_to_order_flow_with_totals(order_flow_files):
    # Customer: register, sign in, and check the token works on the account
    registered = client.post("/customers", json={"name": "Sam Graham", "email": "sam@gmail.com", "password": "secret1", "delivery_address": "755 Academy Way"})
    assert registered.status_code == 201
    customer_id = registered.json()["id"]
    login = client.post("/auth/login", json={"email": "sam@gmail.com", "password": "secret1"})
    assert login.status_code == 200
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    assert client.get(f"/customers/{customer_id}", headers=headers).status_code == 200

    # Menu: read the restaurant and its items from the API
    restaurant = client.get("/restaurants").json()[0]
    assert [item["name"] for item in restaurant["items"]] == ["Burger", "Fries"]

    # Cart: add two items from that menu
    for item_name, quantity in [("Burger", 2), ("Fries", 1)]:
        added = client.post(f"/customers/{customer_id}/cart/items", json={"restaurant_id": restaurant["id"], "item_name": item_name, "quantity": quantity}, headers=headers)
        assert added.status_code == 200
    cart = client.get(f"/customers/{customer_id}/cart", headers=headers).json()
    assert cart["subtotal"] == 24.0
    assert cart["tax"] == 2.88
    assert cart["total"] == 26.88

    # Checkout: the cart passes validation with the same total
    checkout = client.post(f"/customers/{customer_id}/checkout/validate", headers=headers)
    assert checkout.status_code == 200
    assert checkout.json()["total"] == 26.88

    # Order: created from the cart, saved, listed in history, and the cart is emptied
    created = client.post(f"/customers/{customer_id}/orders", headers=headers)
    assert created.status_code == 200
    order = created.json()
    assert order["customer_id"] == customer_id
    assert order["restaurant_id"] == restaurant["id"]
    assert [(i["name"], i["quantity"]) for i in order["items"]] == [("Burger", 2), ("Fries", 1)]
    assert order["total"] == 26.88
    assert order["transaction_id"]
    assert len(order_repo.get_orders()) == 1
    history = client.get(f"/customers/{customer_id}/orders", headers=headers).json()
    assert [o["id"] for o in history] == [order["id"]]
    cart_after = client.get(f"/customers/{customer_id}/cart", headers=headers).json()
    assert cart_after["items"] == []
    assert cart_after["total"] == 0.0



#regression test req fufillment
