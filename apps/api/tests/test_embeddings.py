from app.adapters.embeddings import cosine_similarity, embed_text


def test_embed_text_is_deterministic() -> None:
    a = embed_text("hotel check-in Oct 10")
    b = embed_text("hotel check-in Oct 10")
    assert a == b
    assert len(a) == 64


def test_similar_texts_rank_higher() -> None:
    query = embed_text("check-in date hotel confirmation")
    relevant = embed_text("Hotel check-in Oct 10, 2026 confirmation HT-998877")
    irrelevant = embed_text("flight baggage policy economy cabin")
    assert cosine_similarity(query, relevant) > cosine_similarity(query, irrelevant)
