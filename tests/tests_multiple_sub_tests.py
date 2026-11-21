from uuid import uuid4
from app.services import cart_service
from app.repositories import restaurant_repository
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import customer_repository, restaurant_repository, cart_repo, order_repo
from app.security import hash_password
from app.tokens import create_access_token


client = TestClient(app)


#regression test req fufillment - done by vassili
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





#rayan





