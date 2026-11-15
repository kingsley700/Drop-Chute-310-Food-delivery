import pytest
from app.repositories import customer_repository


@pytest.fixture(autouse=True)
def temp_data_file(tmp_path, monkeypatch):
    test_file = tmp_path / "customers.json"
    test_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(test_file))


def add_Sam():
    return customer_repository.create_customer(
        name="Sam Graham",
        email="SamuelGraham@gmail.com",
        hashed_password="SammyG200",
        delivery_address="755 Academy Way",
    )


def add_Julia():
    return customer_repository.create_customer(
        name="Julia Dew",
        email="JuliaMountain@gmail.com",
        hashed_password="hash456",
        delivery_address="128 University Way",
    )


def test_create_customer_new_id():
    personA = add_Sam()
    personB = add_Julia()
    assert personB.id == personA.id + 1


def test_stored_customer_keeps_hash_only():  # Checks if hashed
    add_Sam()
    stored = customer_repository.get_customer_by_id(1)
    assert stored.hashed_password == "SammyG200"
    assert "password" not in stored.model_dump()


def test_get_customers():  # Checks if returns all customers
    add_Sam()
    add_Julia()
    names = []
    for customer in customer_repository.get_customers():
        names.append(customer.name)
    assert names == ["Sam Graham", "Julia Dew"]


def test_get_customers_is_empty_when_no_customers():
    assert customer_repository.get_customers() == []


def test_get_customer_by_id_returns_customer():
    add_Sam()
    found = customer_repository.get_customer_by_id(1)
    assert found.name == "Sam Graham"


def test_get_customer_by_email_returns_customer():
    add_Sam()
    found = customer_repository.get_customer_by_email("SamuelGraham@gmail.com")
    assert found is not None
    assert found.id == 1


def test_get_customer_by_email_ignores_case():
    add_Sam()
    found = customer_repository.get_customer_by_email("SamuelGraHam@gMAIL.com")
    assert found is not None

def test_empty_data_file_is_handled(tmp_path, monkeypatch):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(empty_file))
    assert customer_repository.get_customers() == []