import pytest

from app.domain.crypto import (
    EncryptionError,
    decrypt_text,
    encrypt_text,
    mask_passport,
    validate_passport_number,
)


def test_encrypt_decrypt_roundtrip() -> None:
    secret = "test-secret-key"
    token = encrypt_text("AB1234567", secret)
    assert token != "AB1234567"
    assert decrypt_text(token, secret) == "AB1234567"


def test_mask_passport() -> None:
    assert mask_passport("AB1234567") == "*****4567"


def test_validate_passport_number() -> None:
    assert validate_passport_number(" ab1234567 ") == "AB1234567"
    with pytest.raises(ValueError):
        validate_passport_number("ab")


def test_decrypt_wrong_key_fails() -> None:
    token = encrypt_text("AB1234567", "key-a")
    with pytest.raises(EncryptionError):
        decrypt_text(token, "key-b")
