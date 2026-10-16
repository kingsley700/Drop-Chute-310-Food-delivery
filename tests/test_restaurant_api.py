import json
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import restaurant_repository as repo
from app.schemas.health import HealthResponse
from app.schemas.restaurantschemas import Restaurant

client = TestClient(app)

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





def test_list_has_menu_items(tmp_path):
    make_file(tmp_path)
    try:
        data={r["id"]:r for r in client.get("/restaurants").json()}
        assert [i["name"]for i in data[1]["items"]]==["Can Pop", "Juice"]
        assert data[3]["items"]==[]
    finally:
        repo.filep=original_path


def test_is_json(tmp_path):
    make_file(tmp_path)
    try:
        assert client.get("/restaurants").headers["content-type"]=="application/json"
    finally:
        repo.filep=original_path


def test_list_has_new_restaurant_after_restart(tmp_path):
    make_file(tmp_path)
    try:
        repo.create_restaurant({"name": "Tossings", "cuisine": "Italian"})
        restarted=TestClient(app)
        data=restarted.get("/restaurants").json()
        assert [r["id"]for r in data]==[1,2,3,4]
        assert data[-1]["name"]=="Tossings"
    finally:
        repo.filep=original_path


def test_list_update_works(tmp_path):
    make_file(tmp_path)
    try:
        repo.update_restaurant_name(1, "Golden Island 2")
        repo.update_restaurant_cuisine(1, "Asian")
        after_update=client.get("/restaurants").json()[0]
        assert after_update["name"]=="Golden Island 2" 
        assert after_update["cuisine"]=="Asian"
    finally:
        repo.filep=original_path


def test_list_delete_works(tmp_path):
    make_file(tmp_path)
    try:
        repo.delete_restaurant(1)
        data=client.get("/restaurants").json()
        assert [r["name"]for r in data]==["Bamboo Chopsticks", "Chipotle"]
        assert [r["id"]for r in data]==[1,2]
    finally:
        repo.filep=original_path


def test_list_returns_seed(tmp_path):
    make_file(tmp_path)
    try:
        response=client.get("/restaurants")
        assert response.status_code==200
        assert [r["id"]for r in response.json()]==[1,2,3]
    finally:
        repo.filep=original_path


def test_list_matches_response(tmp_path):
    make_file(tmp_path)
    try:
        for r in client.get("/restaurants").json():
            Restaurant(**r)
    finally:
        repo.filep=original_path


def test_list_empty_file(tmp_path):
    empty=tmp_path/"empty.json"
    empty.write_text("[]", encoding="utf-8")
    repo.filep=str(empty)
    try:
        response=client.get("/restaurants")
        assert response.status_code==200
        assert response.json()==[]
    finally:
        repo.filep=original_path


def test_list_wrong_method_405(tmp_path):
    make_file(tmp_path)
    try:
        assert client.delete("/restaurants").status_code==405
    finally:
        repo.filep=original_path


def test_unknown_path_404():
    assert client.get("/does-not-exist").status_code==404


def test_return_home_msg():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()=={"message": "Food Delivery Api is running"}


def test_health_matches_response_model():
    response=client.get("/health")
    assert response.status_code==200
    HealthResponse(**response.json())
    assert response.json()=={"status": "Ok"}


def test_docs_available():
    assert client.get("/docs").status_code==200


def test_openapi_documents_health_and_home():
    paths=client.get("/openapi.json").json()["paths"]
    assert paths["/health"]["get"]["summary"]=="Health check"
    assert paths["/"]["get"]["summary"]=="API welcome message"


def test_openapi_documents_restaurants_list():
    operation=client.get("/openapi.json").json()["paths"]["/restaurants"]["get"]
    assert operation["summary"]=="List of all restaurants"
    assert "500" in operation["responses"]
    

def test_missing_file_returns_500(tmp_path):
    repo.filep=str(tmp_path/"missing.json")
    try:
        response=TestClient(app, raise_server_exceptions=False).get("/restaurants")
        assert response.status_code==500
    finally:
        repo.filep=original_path


def test_missing_required_field_returns_500(tmp_path):
    file=make_file(tmp_path)
    file.write_text(json.dumps([{"id": 1, "name": "No Cuisine", "items": []}]), encoding="utf-8")
    try:
        assert TestClient(app, raise_server_exceptions=False).get("/restaurants").status_code==500
    finally:
        repo.filep=original_path
