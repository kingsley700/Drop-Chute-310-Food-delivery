from app.security import hash_password, verify_password
import pytest


def test_hash_differs_from_plain_password():
    hashed = hash_password("PlainPass")
    assert hashed != "PlainPass"
    assert "PlainPass" not in hashed
    
def test_verify_returns_true_for_correct_password():
    hashed = hash_password("PlainPass")
    assert verify_password("PlainPass", hashed) is True


def test_verify_returns_false_for_wrong_password():
    hashed = hash_password("PlainPass")
    assert verify_password("WrongPassword1", hashed) is False


def test_verify_is_case_sensitive():
    hashed = hash_password("PlainPass")
    assert verify_password("plainpass", hashed) is False


def test_two_hashes_of_same_password_differ():
    first = hash_password("PlainPass")
    second = hash_password("PlainPass")
    assert first != second
    assert verify_password("PlainPass", first) is True
    assert verify_password("PlainPass", second) is True


def test_verify_returns_false_for_invalid_hash():
    assert verify_password("PlainPass", "not-a-real-hash") is False