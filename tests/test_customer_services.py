import pytest

from app.exceptions import ConflictError
from app.repositories import customer_repository
from app.schemas.customerschema import CustomerCreate
from app.security import verify_password
from app.services import customer_services


@pytest.fixture(autouse=True) # This marks a function as setup code (like the function directly below) and makes sure it runs before every test in this file
def temp_data_file(tmp_path, monkeypatch): # Gives each test a temp, blank customer file, then resets after completion
    test_file = tmp_path / "customers.json"
    test_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(test_file))
    

def sam_data():
    return CustomerCreate(
        name="Sam Graham",
        email="SamuelGraham@gmail.com",
        password="PlainPass",
        delivery_address="755 Academy Way",
    )
    
def test_register_returns_customer_without_password_or_hash():
    result = customer_services.register_customer(sam_data())
    assert result.id == 1
    assert result.email == "SamuelGraham@gmail.com"
    assert "password" not in result.model_dump()
    assert "hashed_password" not in result.model_dump()


def test_register_stores_hashed_password():
    result = customer_services.register_customer(sam_data())
    stored = customer_repository.get_customer_by_id(result.id)
    assert stored.hashed_password != "PlainPass"
    assert verify_password("PlainPass", stored.hashed_password) is True


def test_register_duplicate_email_raises_conflict():
    customer_services.register_customer(sam_data())
    with pytest.raises(ConflictError):
        customer_services.register_customer(sam_data())


def test_different_emails_both_register():
    customer_services.register_customer(sam_data())
    julia = CustomerCreate(
        name="Julia Dew",
        email="JuliaMountain@gmail.com",
        password="SuperSecret2",
        delivery_address="128 University Way",
    )
    result = customer_services.register_customer(julia)
    assert result.id == 2