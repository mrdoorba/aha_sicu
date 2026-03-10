"""Tests for storage client download URL generation."""

from app.modules.upload.gcs_client import LocalStorageClient


def test_generate_signed_download_url_returns_local_url():
    """Local client returns a URL pointing to the local download endpoint."""
    storage = LocalStorageClient()
    url = storage.generate_signed_download_url("uploads/abc-123/report.csv")
    assert url == "http://localhost:8000/api/v1/upload/local/abc-123/report.csv"


def test_generate_signed_download_url_handles_nested_path():
    """Object names with nested paths are preserved."""
    storage = LocalStorageClient()
    url = storage.generate_signed_download_url("uploads/def-456/my file.xlsx")
    assert "/def-456/my file.xlsx" in url
