import json
from pathlib import Path
from app.schemas.restaurantschemas import Restaurant

# Use python -m pytest -v when testing. NOT pytest -v

#note to self, when looping i=item r=restaurant

real_data=Path(__file__).resolve().parents[1]/"data"/"restaurants.json"

def load_real_data(): #helper method
    return json.loads(real_data.read_text(encoding="utf-8"))




def test_at_least_two_restaurants():
    assert len(load_real_data())>=2


def test_ids_are_unique():
    ids=[r["id"]for r in load_real_data()]
    assert all(isinstance(i, int) for i in ids)
    assert len(ids)==len(set(ids))
    assert ids==sorted(ids)


def test_restaurants_match_pydantic_model():
    for r in load_real_data():
        Restaurant(**r)


def test_name_cuisine_not_blank():
    for r in load_real_data():
        assert r["name"].strip()
        assert r["cuisine"].strip()


def test_menu_items_are_valid():
    for r in load_real_data():
        names=[i["name"]for i in r["items"]]
        assert len(names)==len(set(names)), f"duplicate item in {r["name"]}"
        for i in r["items"]:
            assert i["name"].strip()
            assert i["price"]>=0
