
from uuid import uuid4
from app.services import cart_service
from app.repositories import restaurant_repository
import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import customer_repository, restaurant_repository, cart_repo, order_repo
from app.security import hash_password
from app.tokens import create_access_token
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import cart_repo, customer_repository, order_repo, restaurant_repository
from app.tokens import create_access_token


client = TestClient(app)

#regression test req fufillment - done by vassili
#bug found during dev of epic issue#84, fixed in pull request#178
#178
def test_order_from_different_restaurant_after_clearing_cart(setup):
    cart_service.add_item_to_cart(1, uuid4(), "Burger", 1)
    cart_service.clear_cart(1)
    cart_service.add_item_to_cart(1, uuid4(), "Pizza", 2)

    response = client.post("/customers/1/orders")
    assert response.status_code == 200

#vassili
@pytest.fixture
def setup(tmp_path, monkeypatch):
    #arrange temp files
    for repo, name in [(customer_repository, "customers"), (restaurant_repository, "restaurants"), (cart_repo, "carts"), (order_repo, "orders")]:
        file = tmp_path / f"{name}.json"
        file.write_text("[]")
        monkeypatch.setattr(repo, "filep", str(file))
    #auth
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    #test user
    return customer_repository.create_customer("Test", "test@example.com", hash_password("Password123"), "123 Street")

#tests menu creation, customer actions like cart checkout and order
#added extra comments to walk through what parts were being done here
def test_order_flow(setup):
    #setup user
    customer = setup
    headers = {"Authorization": "Bearer " + create_access_token(customer.id)}
    restaurant = client.post("/CreateRestaurant", json={"name": "Test", "cuisine": "greek"}, headers=headers)
    assert restaurant.status_code == 201
    restaurant_id = restaurant.json()["id"]

    # make yeeero
    assert client.post(f"/restaurants/{restaurant_id}/items", json={"name": "gyro", "price": 15}, headers=headers).status_code == 201
    # customer can add to cart
    assert client.post(f"/customers/{customer.id}/cart/items", json={"restaurant_id": restaurant_id, "item_name": "gyro", "quantity": 2}).status_code == 200
    #customer can checkout
    assert client.post(f"/customers/{customer.id}/checkout/validate").status_code == 200
    #customer has order
    assert client.post(f"/customers/{customer.id}/orders").status_code == 200



#teppei
@pytest.fixture
def unavailable_item_customer(tmp_path, monkeypatch):
    #arrange temp files
    for repo, name in [(customer_repository, "customers"), (restaurant_repository, "restaurants"), (cart_repo, "carts"), (order_repo, "orders")]:
        file = tmp_path / f"{name}.json"
        file.write_text("[]")
        monkeypatch.setattr(repo, "filep", str(file))
    #auth
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    #test user
    return customer_repository.create_customer("Test", "test@example.com", hash_password("Password123"), "123 Street")

def test_unavailable_item_workflow(unavailable_item_customer):
    client=TestClient(app)
    customer=unavailable_item_customer
    customer_url=f"/customers/{customer.id}"

# Sign in and get an access token.
    login=client.post("/auth/login", json={"email": customer.email, "password": "Password123"})
    assert login.status_code==200

# Create a restaurant.
    headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    restaurant=client.post("/CreateRestaurant", json={"name": "McDonalds", "cuisine": "Burger"}, headers=headers)
    assert restaurant.status_code==201

# Create an item.
    restaurant_id=restaurant.json()["id"]
    menu_item=client.post(f"/restaurants/{restaurant_id}/items", json={"name": "French Fries", "price": 5}, headers=headers)
    assert menu_item.status_code==201

# Add two servings of French Fries to the cart.
    cart_url=f"{customer_url}/cart"
    added=client.post(f"{cart_url}/items", json={"restaurant_id": restaurant_id, "item_name": "French Fries", "quantity": 2}, headers=headers)
    assert added.status_code==200

# Mark French Fries as unavailable.
    updated_item=restaurant_repository.update_restaurant_item(UUID(restaurant_id), "French Fries", available=False)
    assert updated_item["available"] is False

# Verify adding more French Fries is rejected
    rejected=client.post(f"{cart_url}/items", json={"restaurant_id": restaurant_id, "item_name": "French Fries", "quantity": 2}, headers=headers)
    assert rejected.status_code==400
    assert rejected.json()["detail"]=="Menu item is unavailable"

# Verify checkout is rejected.
    checkout = client.post(f"{customer_url}/checkout/validate", headers=headers)
    assert checkout.status_code==400
    assert checkout.json()["detail"]=="Menu item unavailable"

# Verify order creation is rejected.
    orders_url=f"{customer_url}/orders"
    order=client.post(orders_url, headers=headers)
    assert order.status_code==400
    assert order.json()["detail"]=="Menu item unavailable"

# Verify order history is empty
    history=client.get(orders_url, headers=headers)
    assert history.status_code==200
    assert history.json()==[]

# Verify cart still contains two servings.
    cart=client.get(cart_url, headers=headers)
    assert cart.status_code==200
    assert cart.json()["items"]==added.json()["items"]


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


