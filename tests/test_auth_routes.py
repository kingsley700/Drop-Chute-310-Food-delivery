import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories import customer_repository
from app.security import hash_password
from app.tokens import verify_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    path = tmp_path / "customers.json"
    path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(customer_repository, "filep", str(path))
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")
    customer_repository.create_customer(
        name="Sam Graham",
        email="sam@gmail.com",
        hashed_password=hash_password("SuperSecret1"),
        delivery_address="755 Academy Way",
    )


def test_login_success_returns_token():
    response = client.post("/auth/login", json={"email": "sam@gmail.com", "password": "SuperSecret1"})

    assert response.status_code == 200
    assert verify_access_token(response.json()["access_token"]) == 1


def test_login_wrong_password_returns_401():
    response = client.post("/auth/login", json={"email": "sam@gmail.com", "password": "WrongPassword"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_unknown_email_returns_same_401():
    response = client.post("/auth/login", json={"email": "nobody@gmail.com", "password": "SuperSecret1"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}