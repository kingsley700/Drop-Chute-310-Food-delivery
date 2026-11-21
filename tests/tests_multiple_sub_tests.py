
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
def menu_order_customer(tmp_path, monkeypatch):
    #point every repository at its own empty temp file, so the test never touches the real data files
    for repo, name in [(customer_repository, "customers"), (restaurant_repository, "restaurants"), (cart_repo, "carts"), (order_repo, "orders")]:
        file = tmp_path / f"{name}.json"
        file.write_text("[]")
        monkeypatch.setattr(repo, "filep", str(file))
    #auth
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    #test restaurant with a two item menu
    restaurant_repository.create_restaurant({"name": "Golden Island", "cuisine": "Chinese", "items": [
        {"name": "Burger", "price": 10.0},
        {"name": "Fries", "price": 4.0},
    ]})
    #test user
    return customer_repository.create_customer("Test", "test@example.com", hash_password("Password123"), "123 Street")

#orders from the menu the customer sees and checks the totals, the saved order and the emptied cart
def test_menu_to_order_totals(menu_order_customer):
    customer = menu_order_customer
    customer_url = f"/customers/{customer.id}"

    #sign in
    login = client.post("/auth/login", json={"email": customer.email, "password": "Password123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": "Bearer " + token}
    #the cart and order routes don't check the token, so this account request is what proves the token is for this customer
    assert client.get(customer_url, headers=headers).status_code == 200

    #read the menu from the API, so the cart uses the restaurant's real id
    restaurant = client.get("/restaurants").json()[0]
    assert restaurant["items"][0]["name"] == "Burger"

    #add 2 burgers and 1 fries to the cart
    for name, quantity in [("Burger", 2), ("Fries", 1)]:
        response = client.post(
            f"{customer_url}/cart/items",
            json={"restaurant_id": restaurant["id"], "item_name": name, "quantity": quantity},
            headers=headers,
        )
        assert response.status_code == 200

    #the last response is the whole cart: 2 x 10 + 1 x 4 = 24, tax is 12% so 2.88
    cart = response.json()
    assert cart["subtotal"] == 24.0
    assert cart["tax"] == 2.88
    assert cart["total"] == 26.88

    #checkout re-reads the menu prices, so its total must match the cart
    checkout = client.post(f"{customer_url}/checkout/validate", headers=headers)
    assert checkout.status_code == 200
    assert checkout.json()["total"] == 26.88

    #the order is built from the cart
    order = client.post(f"{customer_url}/orders", headers=headers)
    assert order.status_code == 200
    assert order.json()["total"] == 26.88
    assert len(order.json()["items"]) == 2

    #the order was saved to the orders file, and the cart was emptied
    assert order_repo.get_orders()[0].id == order.json()["id"]
    assert client.get(f"{customer_url}/cart", headers=headers).json()["items"] == []