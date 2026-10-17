import json
import pytest
from app.repositories import restaurant_repository as repo
from app.services import restaurant_services as service
from app.schemas.restaurantschemas import Restaurant, RestaurantItem

#decided on using a seed so i dont mess with the restaurants.json file. the tests should still function if i edit the numbers
SEED = [
    {"id": 1, "name": "Golden Island", "cuisine": "Chinese", "items": [{
        "name": "Can Pop",
        "price": 2.25
      },
      {
        "name": "Juice",
        "price": 3.29
      },]},
    {"id": 2, "name": "Bamboo Chopsticks", "cuisine": "Vietnamese", "items": [{
        "name": "Appie Platter",
        "price": 30.0,
        "description": "Spring Roll (1) | Salad Rolls (2) | Veggie Egg Rolls (2) | Coconut Prawns (4) | Golden Wontons (5) | Chicken Wings (4)"
      },
      {
        "name": "Fresh Salad Rolls • Goi Cuon",
        "price": 11.0,
        "description": "Cold rolls with vermicelli, cucumber, beansprouts & lettuce, wrapped inside rice paper with steamed prawn & pork. Served with peanut sauce"
      }]},
    {"id": 3, "name": "Chipotle", "cuisine": "Mexican", "items": []},
]

original_path=repo.filep #so i dont mess with restaurants.json
def make_file(tmp_path): #helper function
    file=tmp_path/"restaurant.json"
    file.write_text(json.dumps(SEED), encoding="utf-8")
    repo.filep=str(file)
    return file

def read_file(file): #helper function
    return json.loads(file.read_text(encoding="utf-8"))


def test_services_get_restaurants_returns_all(tmp_path):
    make_file(tmp_path)
    try:
        assert [r["id"]for r in service.get_restaurants()]==[1,2,3]
    finally:
        repo.filep=original_path


def test_services_get_restaurants_by_ID(tmp_path):
    make_file(tmp_path)
    try:
        assert service.get_restaurant_by_id(2)["name"]=="Bamboo Chopsticks"
    finally:
        repo.filep=original_path


def test_services_get_restaurants_unknown_returns_none(tmp_path):
    try:
        assert service.get_restaurant_by_id(999) is None
    finally:
        repo.filep=original_path


def test_services_get_restaurants_by_name(tmp_path):
    make_file(tmp_path)
    try:
        assert service.get_restaurant_by_name("Bamboo Chopsticks")["cuisine"]=="Vietnamese"
    finally:
        repo.filep=original_path


def test_services_create_restaurant_works(tmp_path):
    file=make_file(tmp_path)
    try:
        new_restaurant=Restaurant(id=0, name="Tossings", cuisine="Italian", items=[])
        created_restaurant=service.create_restaurant(new_restaurant)
        assert created_restaurant["id"] not in (0,1,2,3)
        assert read_file(file)[-1]["name"]=="Tossings"
    finally:
        repo.filep=original_path


def test_services_update_name_persists(tmp_path):
    file=make_file(tmp_path)
    try:
        service.update_restaurant_name(1, "Golden Island 2")
        assert read_file(file)[0]["name"]=="Golden Island 2"
    finally:
        repo.filep=original_path


def test_services_update_cuisine_persists(tmp_path):
    file=make_file(tmp_path)
    try:
        service.update_restaurant_cuisine(3, "Korean")
        assert read_file(file)[2]["cuisine"]=="Korean"
    finally:
        repo.filep=original_path


def test_services_update_unknown_returns_none(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        assert service.update_restaurant_name(999, "Tossings") is None
        assert service.update_restaurant_cuisine(999, "Korean") is None
        assert read_file(file)==before_update
    finally:
        repo.filep=original_path


def test_services_delete_restaurant(tmp_path):
    file=make_file(tmp_path)
    try:
        assert service.delete_restaurant(2) is True
        assert "Bamboo Chopsticks" not in [r["name"] for r in read_file(file)]
    finally:
        repo.filep=original_path


def test_service_delete_unknown_returns_none(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        assert service.delete_restaurant(999) is False
        assert read_file(file)==before_update
    finally:
        repo.filep=original_path


def test_services_add_item_goes_to_correct_restaurant(tmp_path):
    file=make_file(tmp_path)
    try:
        before_add=read_file(file)
        service.add_restaurant_items(3, RestaurantItem(name="Burrito", price=21.0))
        after_add=read_file(file)
        assert [i["name"] for i in after_add[2]["items"]]==["Burrito"]
        assert after_add[0]==before_add[0]
        assert after_add[1]==before_add[1]
    finally:
        repo.filep=original_path


def test_services_add_item_description_is_none(tmp_path):
    file=make_file(tmp_path)
    try:
        service.add_restaurant_items(3, RestaurantItem(name="Burrito", price=21.0))
        assert read_file(file)[2]["items"][0]=={"name": "Burrito", "price": 21.0, "description": None}
    finally:
        repo.filep=original_path


def test_services_add_item_to_unknown_restaurant_changes_nothing(tmp_path):
    file=make_file(tmp_path)
    try:
        before_add=read_file(file)
        assert service.add_restaurant_items(999, RestaurantItem(name="donut", price=1.0)) is None
        assert read_file(file)==before_add
    finally:
        repo.filep=original_path


def test_services_update_item_persists(tmp_path):
    file=make_file(tmp_path)
    try:
        service.update_restaurant_item(1, "Can Pop", new_name="Soda", price=3.0, description="Sweet")
        assert read_file(file)[0]["items"][0]=={"name": "Soda", "price": 3.0, "description": "Sweet"}
    finally:
        repo.filep=original_path


def test_services_partial_update_keeps_other_values(tmp_path):
    file=make_file(tmp_path)
    try:
        service.update_restaurant_item(1, "Can Pop", price=3.0)
        assert read_file(file)[0]["items"][0]=={"name": "Can Pop", "price": 3.0}
    finally:
        repo.filep=original_path


def test_services_update_item_unknown_returns_none(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        assert service.update_restaurant_item(1, "Donut", price=1.0) is None
        assert service.update_restaurant_item(999, "Can Pop", price=1.0) is None
        assert read_file(file)==before_update
    finally:
        repo.filep=original_path


def test_services_delete_item(tmp_path):
    file=make_file(tmp_path)
    try:
        service.delete_restaurant_item(1, "Can Pop")
        assert [i["name"] for i in read_file(file)[0]["items"]]==["Juice"]
    finally:
        repo.filep=original_path


def test_services_delete_unknown_item_changes_nothing(tmp_path):
    file=make_file(tmp_path)
    try:
        before_delete=read_file(file)
        service.delete_restaurant_item(1, "Donut")
        assert read_file(file)==before_delete
    finally:
        repo.filep=original_path


def test_services_swap_ID_stays_sorted(tmp_path):
    file=make_file(tmp_path)
    try:
        service.swap_restaurant_id(1,3)
        restaurants=read_file(file)
        assert[r["id"] for r in restaurants]==[1,2,3]
        assert restaurants[0]["name"]=="Chipotle"
    finally:
        repo.filep=original_path