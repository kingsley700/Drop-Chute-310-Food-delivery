import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import customer_repository
from app.tokens import create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    path = tmp_path / "customers.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(path))
    monkeypatch.setenv(
        "JWT_SECRET_KEY", "test-this-long-ahh-key-that-is-long-enough-for-hs256"
    )
    customer_repository.create_customer(
        "Sam Graham", "sam@gmail.com", "hash1", "755 Academy Way"
    )
    customer_repository.create_customer(
        "Alex Roy", "alex@gmail.com", "hash2", "12 Main Street"
    )


def auth(customer_id):
    return {"Authorization": "Bearer " + create_access_token(customer_id)}


def test_view_own_account():
    response = client.get("/customers/1", headers=auth(1))

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Sam Graham",
        "email": "sam@gmail.com",
        "delivery_address": "755 Academy Way",
    }


def test_update_own_delivery_address():
    response = client.patch(
        "/customers/1", json={"delivery_address": "99 New Road"}, headers=auth(1)
    )

    assert response.status_code == 200
    assert response.json()["delivery_address"] == "99 New Road"
    assert (
        client.get("/customers/1", headers=auth(1)).json()["delivery_address"]
        == "99 New Road"
    )


def test_someone_elses_account_returns_403():
    assert client.get("/customers/2", headers=auth(1)).status_code == 403
    assert (
        client.patch(
            "/customers/2", json={"delivery_address": "Hacked"}, headers=auth(1)
        ).status_code
        == 403
    )


def test_nonexistent_account_returns_404():
    response = client.get("/customers/999", headers=auth(999))

    assert response.status_code == 404
