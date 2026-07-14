"""Tests for file download endpoint."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


AUTH_HEADERS = {"Authorization": "Bearer valid-token"}

MOCK_USER = {
    "id": 1,
    "firebase_uid": "test-uid",
    "email": "test@example.com",
    "role": "member",
    "created_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "last_login": datetime(2026, 2, 5, tzinfo=timezone.utc),
}

SAMPLE_UPLOAD_WITH_PATH = {
    "id": 1,
    "brand_id": 123,
    "file_type": "cpc_ad_report",
    "calculator_target": "ads_keyword",
    "filename": "Brand_report.csv",
    "file_size": 1024,
    "row_count": 25,
    "parsed_data": {"rows": []},
    "uploaded_at": datetime(2026, 3, 10, tzinfo=timezone.utc),
    "storage_path": "uploads/abc-123/report.csv",
}

SAMPLE_UPLOAD_NO_PATH = {
    **SAMPLE_UPLOAD_WITH_PATH,
    "storage_path": None,
}


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_download_returns_signed_url(client):
    """Download endpoint returns a signed URL for an existing upload."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_UPLOAD_WITH_PATH)

        mock_storage = MagicMock()
        mock_storage.generate_signed_download_url.return_value = (
            "https://storage.example.com/signed-download-url"
        )
        mock_storage_fn.return_value = mock_storage

        resp = client.get(
            "/api/v1/upload/brands/123/download/cpc_ad_report",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["download_url"] == "https://storage.example.com/signed-download-url"
    assert body["filename"] == "Brand_report.csv"


def test_download_gcs_failure_returns_502(client):
    """A GCS error while minting the download URL surfaces as 502, not a bare 500."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_UPLOAD_WITH_PATH)

        mock_storage = MagicMock()
        mock_storage.generate_signed_download_url.side_effect = RuntimeError("GCS unavailable")
        mock_storage_fn.return_value = mock_storage

        resp = client.get(
            "/api/v1/upload/brands/123/download/cpc_ad_report",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 502
    assert resp.json()["code"] == "UPLOAD_SIGNED_URL_FAILED"


def test_download_returns_404_when_no_upload(client):
    """Download endpoint returns 404 if no file uploaded for this slot."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)

        resp = client.get(
            "/api/v1/upload/brands/123/download/cpc_ad_report",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 404


def test_download_returns_404_when_no_storage_path(client):
    """Download endpoint returns 404 if upload exists but has no storage_path."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_UPLOAD_NO_PATH)

        resp = client.get(
            "/api/v1/upload/brands/123/download/cpc_ad_report",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 404


def test_local_download_serves_file(client):
    """Local download endpoint serves file bytes in dev mode."""
    from app.modules.upload.gcs_client import LocalStorageClient, make_object_name

    storage = LocalStorageClient()
    object_name = make_object_name("test-dl-id", "report.csv")
    file_path = storage._base_dir / object_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"col1,col2\nval1,val2\n")

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        resp = client.get(
            "/api/v1/upload/local/test-dl-id/report.csv",
            headers=AUTH_HEADERS,
        )

    assert resp.status_code == 200
    assert resp.content == b"col1,col2\nval1,val2\n"

    # Cleanup
    file_path.unlink(missing_ok=True)
