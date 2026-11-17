import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import customer_repository

client = TestClient(app)


def valid_body():
    return {
        "name": "Sam Graham",
        "email": "SamuelGraham@gmail.com",
        "password": "SuperSecret1",
        "delivery_address": "755 Academy Way",
    }


@pytest.fixture(autouse=True)
def temp_data_file(tmp_path, monkeypatch):
    """Point the repository at an empty temp file so tests never touch data/customers.json."""
    path = tmp_path / "customers.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(path))
    return path


def test_register_returns_201_with_customer_and_no_password():
    response = client.post("/customers", json=valid_body())

    assert response.status_code == 201
    body = response.json()
    assert body == {
        "id": 1,
        "name": "Sam Graham",
        "email": "SamuelGraham@gmail.com",
        "delivery_address": "755 Academy Way",
    }
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_409():
    client.post("/customers", json=valid_body())

    response = client.post("/customers", json=valid_body())

    assert response.status_code == 409
    assert response.json() == {"detail": "Email is already registered"}


@pytest.mark.parametrize("missing", ["name", "email", "password", "delivery_address"])
def test_register_missing_field_returns_422(missing):
    body = valid_body()
    del body[missing]

    response = client.post("/customers", json=body)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", "Al"),
        ("name", "   "),
        ("email", "not-an-email"),
        ("password", "short"),
        ("password", "x" * 73),
        ("delivery_address", ""),
        ("delivery_address", "   "),
    ],
)
def test_register_invalid_field_returns_422(field, value):
    body = valid_body()
    body[field] = value

    response = client.post("/customers", json=body)

    assert response.status_code == 422


def test_register_invalid_input_does_not_save_anything(temp_data_file):
    body = valid_body()
    body["password"] = "short"
    client.post("/customers", json=body)

    assert json.loads(temp_data_file.read_text(encoding="utf-8")) == []


def test_422_does_not_echo_the_password_back():
    body = valid_body()
    body["password"] = "abc12"  # too short, so FastAPI would normally echo it as "input"

    response = client.post("/customers", json=body)

    assert response.status_code == 422
    assert "abc12" not in response.text
    for error in response.json()["detail"]:
        assert "input" not in error


def test_all_response_codes_are_documented():
    spec = client.get("/openapi.json").json()

    documented = spec["paths"]["/customers"]["post"]["responses"]

    assert "201" in documented
    assert "409" in documented
    assert "422" in documented