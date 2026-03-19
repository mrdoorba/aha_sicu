"""Tests for application configuration parsing."""

from unittest.mock import patch

from app.config import Settings


def test_cors_origin_list_parses_comma_separated():
    """cors_origin_list should parse comma-separated origins into a list."""
    with patch.dict("os.environ", {"CORS_ORIGINS": "https://a.com,https://b.com"}):
        s = Settings()
    assert s.cors_origin_list == ["https://a.com", "https://b.com"]


def test_cors_origin_list_strips_whitespace():
    """cors_origin_list should strip whitespace from each origin."""
    with patch.dict("os.environ", {"CORS_ORIGINS": "https://a.com , https://b.com "}):
        s = Settings()
    assert s.cors_origin_list == ["https://a.com", "https://b.com"]


def test_cors_origin_list_default_includes_localhost():
    """Default CORS origins should include localhost for local dev."""
    with patch.dict("os.environ", {}, clear=False):
        s = Settings(_env_file=None)
    assert "http://localhost:5173" in s.cors_origin_list
    assert "http://localhost:4173" in s.cors_origin_list
