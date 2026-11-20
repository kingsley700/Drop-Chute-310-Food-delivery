
import json
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.main import app
from app.exceptions import ConflictError
from app.repositories import customer_repository as repo
from app.schemas.customerschema import CustomerCreate
from app.security import verify_password
from app.services import customer_services as service


client = TestClient(app)


# Setup
@pytest.fixture(autouse=True)
def temp_data_file(tmp_path, monkeypatch):
    path = tmp_path / "customers.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(repo, "filep", str(path))
    return path


def valid_data():
    return {
        "name": "Sam Graham",
        "email": "SamuelGraham@gmail.com",
        "password": "SuperSecret1",
        "delivery_address": "755 Academy Way",
    }


def add_customer(name="Sam Graham", email="SamuelGraham@gmail.com"):
    return repo.create_customer(name, email, "hashed123", "755 Academy Way")


# Schema tests
@pytest.mark.parametrize("field, value", [
    ("email", "invalid"),
    ("name", "Al"),
    ("name", "   "),
    ("password", "short"),
    ("password", "x" * 73),
    ("delivery_address", ""),
    ("delivery_address", "   "),
])
def test_invalid_registration_data(field, value):
    data = valid_data()
    data[field] = value
    with pytest.raises(ValidationError):
        CustomerCreate(**data)


@pytest.mark.parametrize("field", ["name", "email", "password", "delivery_address"])
def test_missing_registration_data(field):
    data = valid_data()
    del data[field]
    with pytest.raises(ValidationError):
        CustomerCreate(**data)


# Repository tests
def test_create_and_get_customers():
    first = add_customer()
    second = add_customer("Julia Dew", "julia@example.com")

    assert first.id == 1
    assert second.id == 2
    assert len(repo.get_customers()) == 2
    assert repo.get_customer_by_id(1).name == "Sam Graham"


def test_get_customer_by_id_not_found():
    assert repo.get_customer_by_id(99) is None


def test_get_customer_by_email():
    add_customer()
    assert repo.get_customer_by_email("  SAMUELGRAHAM@GMAIL.COM  ").id == 1
    assert repo.get_customer_by_email("missing@example.com") is None


def test_empty_customer_file(temp_data_file):
    temp_data_file.write_text("", encoding="utf-8")
    assert repo.get_customers() == []


# Service tests
def test_register_customer():
    result = service.register_customer(CustomerCreate(**valid_data()))
    stored = repo.get_customer_by_id(result.id)

    assert result.id == 1
    assert "password" not in result.model_dump()
    assert "hashed_password" not in result.model_dump()
    assert verify_password("SuperSecret1", stored.hashed_password)


def test_duplicate_email_raises_conflict():
    service.register_customer(CustomerCreate(**valid_data()))
    data = valid_data()
    data["email"] = "SAMUELGRAHAM@GMAIL.COM"

    with pytest.raises(ConflictError):
        service.register_customer(CustomerCreate(**data))


def test_different_emails_register():
    service.register_customer(CustomerCreate(**valid_data()))
    data = valid_data()
    data["email"] = "julia@example.com"

    assert service.register_customer(CustomerCreate(**data)).id == 2


# API tests
def test_register_customer():
    response = client.post("/customers", json=valid_data())

    assert response.status_code == 201
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()


def test_duplicate_email_returns_409():
    client.post("/customers", json=valid_data())
    assert client.post("/customers", json=valid_data()).status_code == 409


@pytest.mark.parametrize("field", ["name", "email", "password", "delivery_address"])
def test_invalid_registration_returns_422(field):
    data = valid_data()
    del data[field]
    assert client.post("/customers", json=data).status_code == 422


@pytest.mark.parametrize("field, value", [
    ("email", "invalid"),
    ("name", "Al"),
    ("name", "   "),
    ("password", "short"),
    ("password", "x" * 73),
    ("delivery_address", ""),
])
def test_invalid_field_returns_422(field, value):
    data = valid_data()
    data[field] = value
    assert client.post("/customers", json=data).status_code == 422


def test_invalid_registration_does_not_save(temp_data_file):
    data = valid_data()
    data["password"] = "short"
    client.post("/customers", json=data)
    assert json.loads(temp_data_file.read_text()) == []


def test_response_codes_documented():
    spec = client.get("/openapi.json").json()
    responses = spec["paths"]["/customers"]["post"]["responses"]
    assert all(code in responses for code in ["201", "409", "422"])
