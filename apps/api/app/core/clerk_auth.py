from __future__ import annotations

from typing import Any

import jwt
from jwt import PyJWKClient


def verify_clerk_token(token: str, clerk_secret_key: str) -> dict[str, Any]:
    """Verify a Clerk session JWT and return its claims."""
    unverified = jwt.decode(token, options={"verify_signature": False})
    jwks_url = unverified.get("iss", "")
    if jwks_url:
        jwks_client = PyJWKClient(f"{jwks_url}/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

    return jwt.decode(token, clerk_secret_key, algorithms=["HS256"])
