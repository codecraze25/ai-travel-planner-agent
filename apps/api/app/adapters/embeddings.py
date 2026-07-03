from __future__ import annotations

import hashlib
import math
import re

EMBEDDING_DIM = 64


def embed_text(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """Deterministic bag-of-tokens embedding for offline RAG (no API key)."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vector = [0.0] * dim
    if not tokens:
        return vector
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))
