from datetime import timedelta

import pytest

from app.exceptions import AuthenticationError
from app.tokens import create_access_token, verify_access_token


@pytest.fixture(autouse=True)
def secret_key(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")


def test_valid_token_verifies_to_the_customer_id():
    token = create_access_token(7)

    assert verify_access_token(token) == 7


def test_expired_token_is_rejected():
    token = create_access_token(7, expires_delta=timedelta(seconds=-1))

    with pytest.raises(AuthenticationError):
        verify_access_token(token)


def test_tampered_token_is_rejected():
    token = create_access_token(7)
    header, payload, signature = token.split(".")
    if signature[0] == "A":
        bad_signature = "B" + signature[1:]
    else:
        bad_signature = "A" + signature[1:]

    with pytest.raises(AuthenticationError):
        verify_access_token(header + "." + payload + "." + bad_signature)