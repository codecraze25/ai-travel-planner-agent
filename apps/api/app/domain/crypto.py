"""Field-level encryption for sensitive profile data (AES via Fernet)."""

from __future__ import annotations

import base64
import hashlib
import re

from cryptography.fernet import Fernet, InvalidToken


class EncryptionError(ValueError):
    """Raised when encryption/decryption fails."""


def derive_fernet_key(secret: str) -> bytes:
    """Derive a stable Fernet key from an app secret."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(plaintext: str, secret: str) -> str:
    if not plaintext:
        raise EncryptionError("Cannot encrypt empty value.")
    if not secret:
        raise EncryptionError("PROFILE_ENCRYPTION_KEY is not configured.")
    token = Fernet(derive_fernet_key(secret)).encrypt(plaintext.encode("utf-8"))
    return token.decode("ascii")


def decrypt_text(ciphertext: str, secret: str) -> str:
    if not ciphertext:
        raise EncryptionError("Cannot decrypt empty value.")
    if not secret:
        raise EncryptionError("PROFILE_ENCRYPTION_KEY is not configured.")
    try:
        return Fernet(derive_fernet_key(secret)).decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise EncryptionError("Failed to decrypt sensitive field.") from exc


def mask_passport(passport_number: str) -> str:
    """Show only last 4 characters for UI display."""
    cleaned = re.sub(r"\s+", "", passport_number)
    if len(cleaned) <= 4:
        return "****"
    return f"{'*' * (len(cleaned) - 4)}{cleaned[-4:]}"


def validate_passport_number(passport_number: str) -> str:
    cleaned = passport_number.strip().upper()
    if len(cleaned) < 5 or len(cleaned) > 20:
        raise ValueError("Passport number must be 5–20 characters.")
    if not re.fullmatch(r"[A-Z0-9]+", cleaned):
        raise ValueError("Passport number may only contain letters and digits.")
    return cleaned
