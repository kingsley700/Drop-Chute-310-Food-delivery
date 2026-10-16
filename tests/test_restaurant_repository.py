import json
import pytest
from app.repositories import restaurant_repository as repo

# Use python -m pytest -v when testing. NOT pytest -v

#note to self, when looping i=item r=restaurant

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

original_path=repo.filep #helper function
def make_file(tmp_path):
    file=tmp_path/"restaurant.json"
    file.write_text(json.dumps(SEED), encoding="utf-8")
    repo.filep=str(file)
    return file

def read_file(file): #helper function
    return json.loads(file.read_text(encoding="utf-8"))




def test_restaurant_unknown(tmp_path):
    make_file(tmp_path)
    try:
        assert repo.get_restaurant(999) is None
    finally:
        repo.filep=original_path


def test_restaurant_returns_all(tmp_path):
    make_file(tmp_path)
    try:
        ids=[r["id"] for r in repo.get_restaurants()]
        assert ids==[1,2,3]
    finally:
        repo.filep=original_path


def test_restaurant_ID(tmp_path):
    make_file(tmp_path)
    try:
        assert repo.get_restaurant(2)["name"]=="Bamboo Chopsticks"
    finally:
        repo.filep=original_path


def test_create_restaurant_works(tmp_path):
    file=make_file(tmp_path)
    try:
        create=repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        assert create["id"] not in (1,2,3)
        assert create["items"]==[]
        assert read_file(file)[-1]["name"]=="Tossings"
    finally:
        repo.filep=original_path


def test_create_doesnt_mutate(tmp_path): #replace x
    make_file(tmp_path)
    try:
        x=({"name": "Tossings", "cuisine": "Italian"})
        repo.create_restaurant(x)
        assert "id" not in x
    finally:
        repo.filep=original_path


def test_updated_name_persists(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.update_restaurant_name(1, "Golden Island 2")
        assert read_file(file)[0]["name"]=="Golden Island 2"
    finally:
        repo.filep=original_path


def test_updated_cuisine_persists(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.update_restaurant_cuisine(3, "Italian")
        assert read_file(file)[2]["cuisine"]=="Italian"
    finally:
        repo.filep=original_path


def test_update_only_changes_targeted(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        repo.update_restaurant_cuisine(1, "Italian")
        after_update=read_file(file)
        assert after_update[1:]==before_update[1:]
        assert after_update[0]["items"]==before_update[0]["items"]
    finally:
        repo.filep=original_path


def test_update_unknown_returns_none(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        assert repo.update_restaurant_name(999, "X") is None
        assert repo.update_restaurant_cuisine(999, "X") is None
        assert read_file(file)==before_update
    finally:
        repo.filep=original_path


def test_delete_restaurant_removes(tmp_path):
    file=make_file(tmp_path)
    try:
        assert repo.delete_restaurant(2) is True
        names=[r["name"] for r in read_file(file)] 
        assert "Bamboo Chopsticks" not in names
    finally:
        repo.filep=original_path


def test_delete_unknown_returns_false(tmp_path):
    file=make_file(tmp_path)
    try:
        before_delete=read_file(file)
        assert repo.delete_restaurant(999) is False
        assert read_file(file)==before_delete
    finally:
        repo.filep=original_path


def test_ID_unique_after_create(tmp_path):
    make_file(tmp_path)
    try:
        restaurant_1=repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        restaurant_2=repo.create_restaurant({"name": "Tossings2", "cuisine": "Italian2"})
        assert restaurant_1["id"] not in (1,2,3)
        assert restaurant_2["id"] not in (1,2,3)
        assert restaurant_1["id"]!=restaurant_2["id"]
    finally:
        repo.filep=original_path


def test_create_doesnt_affect_other_ID(tmp_path):
    make_file(tmp_path)
    try:
        repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        assert [r["id"] for r in repo.get_restaurants()][:3]==[1,2,3]
    finally:
        repo.filep=original_path


def test_ID_persists_to_disk(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        ids_repo=[r["id"]for r in repo.get_restaurants()]
        ids_disk=[r["id"]for r in read_file(file)]
        assert ids_disk==ids_repo
    finally:
        repo.filep=original_path



def test_delete_renumbers_ID(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.delete_restaurant(1)
        data=read_file(file)
        assert [r["id"]for r in data]==[1,2]
        assert [r["name"]for r in data]==["Bamboo Chopsticks", "Chipotle"]
    finally:
        repo.filep=original_path


def test_create_after_delete_has_ID(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.delete_restaurant(1)
        restaurant=repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        ids= [r["id"]for r in repo.get_restaurants()]
        assert ids==[1,2,3]
        assert len(ids)==len(set(ids))
        assert restaurant["id"]==3
    finally:
        repo.filep=original_path


def test_add_item_goes_to_restaurant(tmp_path):
    file=make_file(tmp_path)
    try:
        before_add=read_file(file)
        repo.add_restaurant_items(3,{"name": "Lasagna", "price": 14.0})
        after_add=read_file(file)
        data={r["id"]:r for r in after_add}
        assert [i["name"]for i in data[3]["items"]]==["Lasagna"]
        assert after_add[0]==before_add[0]
        assert after_add[1]==before_add[1]
    finally:
        repo.filep=original_path


def test_add_item_to_unknown_restaurant(tmp_path):
    file=make_file(tmp_path)
    try:
        before_add=read_file(file)
        assert repo.add_restaurant_items(999,{"name": "Lasagna", "price": 67.0}) is None
        assert read_file(file)==before_add
    finally:
        repo.filep=original_path


def test_update_restaurant_item(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.update_restaurant_item(1, "Can Pop", new_name="Soda", price=3.0, description="Sweet")
        updated_item=read_file(file)[0]["items"][0]
        assert updated_item=={"name": "Soda", "price": 3.0, "description": "Sweet"}
    finally:
        repo.filep=original_path


def test_partial_update_restaurant_item_keeps_other_values(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.update_restaurant_item(1, "Can Pop", new_name="Soda")
        updated_item=read_file(file)[0]["items"][0]
        assert updated_item=={"name": "Soda", "price": 2.25}
    finally:
        repo.filep=original_path


def test_update_unknown_restaurant_item(tmp_path):
    file=make_file(tmp_path)
    try:
        before_update=read_file(file)
        assert repo.update_restaurant_item(1, "Donut", price=1.0) is None
        assert repo.update_restaurant_item(999, "Can Pop", price=2.25) is None
        assert read_file(file)==before_update

    finally:
        repo.filep=original_path


def test_delete_item(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.delete_restaurant_item(1,"Can Pop")
        item_names=[i["name"]for i in read_file(file)[0]["items"]]
        assert item_names==["Juice"]
    finally:
        repo.filep=original_path


def test_delete_unknown_item_changes_nothing(tmp_path):
    file=make_file(tmp_path)
    try:
        before_delete=read_file(file)
        repo.delete_restaurant_item(1,"Donut")
        assert before_delete==read_file(file)
    finally:
        repo.filep=original_path


def test_swap_ID_stays_sorted(tmp_path):
    file=make_file(tmp_path)
    try:
        repo.swap_restaurant_id(1,3)
        data=read_file(file)
        assert[r["id"]for r in data]==[1,2,3]
        assert data[0]["name"]=="Chipotle"
    finally:
        repo.filep=original_path


def test_swap_unknown_returns_none(tmp_path):
    file=make_file(tmp_path)
    try:
        before_swap=read_file(file)
        assert repo.swap_restaurant_id(1,999) is None
        assert read_file(file)==before_swap
    finally:
        repo.filep=original_path


def test_missing_file(tmp_path):
    repo.filep=str(tmp_path/"notRestaurants.json")
    try:
        with pytest.raises(FileNotFoundError):
            repo.get_restaurants()
    finally:
        repo.filep = original_path


def test_corrupt_json(tmp_path):
    bad_json=tmp_path/"notRestaurants.json"
    bad_json.write_text("{not valid json", encoding="utf-8")
    repo.filep=str(bad_json)
    try:
        with pytest.raises(json.JSONDecodeError):
            repo.get_restaurants()
    finally:
        repo.filep=original_path