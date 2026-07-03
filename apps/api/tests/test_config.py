from app.core.config import Settings


def test_cors_origin_list_parses_csv() -> None:
    settings = Settings(CORS_ORIGINS="http://localhost:3000, http://localhost:3001")
    assert settings.cors_origin_list == [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


def test_default_mock_providers_enabled() -> None:
    settings = Settings()
    assert settings.use_mock_providers is True
