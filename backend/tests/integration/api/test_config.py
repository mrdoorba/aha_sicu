"""Tests for GET /api/v1/config/features endpoint."""

from unittest.mock import patch

from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_email_enabled_false_when_setting_disabled():
    """Feature flags endpoint returns email_enabled=false when setting is off."""
    with patch("app.modules.config.router.settings") as mock_settings:
        mock_settings.email_enabled = False
        response = client.get("/api/v1/config/features")

    assert response.status_code == 200
    assert response.json() == {"email_enabled": False}


def test_email_enabled_true_when_setting_enabled():
    """Feature flags endpoint returns email_enabled=true when setting is on."""
    with patch("app.modules.config.router.settings") as mock_settings:
        mock_settings.email_enabled = True
        response = client.get("/api/v1/config/features")

    assert response.status_code == 200
    assert response.json() == {"email_enabled": True}
