import pytest
from pydantic import ValidationError
from app.schemas.customerschema import Customer, CustomerCreate, CustomerResponse


def valid_payload():
    return {
        "name": "Samuel Graham",
        "email": "SamuelGraham@gmail.com",
        "password": "SammyG200",
        "delivery_address": "755 Academy Way",
    }


def test_valid_registration_input():
    customer = CustomerCreate(**valid_payload())
    assert customer.email == "SamuelGraham@gmail.com"


def test_password_length_limits():
    payload = valid_payload()

    payload["password"] = "a" * 101
    with pytest.raises(ValidationError):
        CustomerCreate(**payload)

    payload["password"] = "a" * 6
    CustomerCreate(**payload)

    payload["password"] = "a" * 100
    CustomerCreate(**payload)


def test_invalid_email_rejected():  # Replaces email with invalid one, then tests if can be created
    payload = valid_payload()
    payload["email"] = "GarbageEmail"
    with pytest.raises(ValidationError):
        CustomerCreate(**payload)


def test_missing_fields_rejected():  # Deletes a field one at a time, outputs that there are missing fields
    for field in ["name", "email", "password", "delivery_address"]:
        payload = valid_payload()
        del payload[field]
        with pytest.raises(ValidationError):
            CustomerCreate(**payload)


def test_blank_name_rejected():  # Sets name to spaces, then tries creating a customer
    payload = valid_payload()
    payload["name"] = "   "
    with pytest.raises(ValidationError):
        CustomerCreate(**payload)


def test_response_schema_has_no_password_or_hash():  # Make sure response schema doesn't include (hashed/) password
    fields = CustomerResponse.model_fields
    assert "password" not in fields
    assert "hashed_password" not in fields


def test_response_built_from_stored_customer_drops_hash():  # Ensures that hashed password is dropped in response
    stored = Customer(
        id=1,
        name="Sam Lee",
        email="sam@example.com",
        hashed_password="placeholder",
        delivery_address="755 Academy Way",
    )
    response = CustomerResponse(**stored.model_dump())
    assert "hashed_password" not in response.model_dump()
