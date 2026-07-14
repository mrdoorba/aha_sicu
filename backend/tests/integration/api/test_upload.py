"""Integration tests for upload API endpoints."""

from contextlib import asynccontextmanager
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

SAMPLE_BRAND = {
    "id": 123,
    "brand_name": "Brand ABC",
    "raw_data": {},
    "updated_at": datetime(2026, 2, 5, tzinfo=timezone.utc),
    "meeting_raw_data": None,
}

SAMPLE_UPLOAD = {
    "id": 1,
    "brand_id": 123,
    "file_type": "cpc_ad_report",
    "calculator_target": "ads_keyword",
    "filename": "report.csv",
    "file_size": 1024,
    "row_count": 50,
    "uploaded_at": datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
}

SAMPLE_PENDING = {
    "upload_id": "test-uuid-1234",
    "brand_id": 123,
    "file_type": "cpc_ad_report",
    "filename": "report.csv",
    "content_type": "text/csv",
    "object_name": "uploads/test-uuid-1234/report.csv",
    "expires_at": datetime(2099, 1, 1, tzinfo=timezone.utc),
    "created_at": datetime(2026, 3, 19, tzinfo=timezone.utc),
}


def _make_transactional_conn(fetchrow_side_effect=None, fetch_return=None):
    """Create a mock connection with transaction support."""
    mock_conn = AsyncMock()
    if fetchrow_side_effect is not None:
        mock_conn.fetchrow = AsyncMock(side_effect=fetchrow_side_effect)
    if fetch_return is not None:
        mock_conn.fetch = AsyncMock(return_value=fetch_return)

    @asynccontextmanager
    async def mock_transaction():
        yield

    mock_conn.transaction = mock_transaction
    return mock_conn


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


# ---------------------------------------------------------------------------
# POST /api/v1/upload/signed-url
# ---------------------------------------------------------------------------

def test_signed_url_valid(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Brand lookup
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_BRAND)

        # Pending queries mocks
        mock_pending_queries.cleanup_expired_uploads = AsyncMock(return_value=0)
        mock_pending_queries.create_pending_upload = AsyncMock(return_value=SAMPLE_PENDING)

        # Storage mock
        mock_storage = MagicMock()
        mock_storage.generate_signed_upload_url.return_value = "https://storage.googleapis.com/test-signed-url"
        mock_storage_fn.return_value = mock_storage

        response = client.post("/api/v1/upload/signed-url", json={
            "filename": "report.csv",
            "content_type": "text/csv",
            "file_type": "cpc_ad_report",
            "brand_id": 123,
        }, headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert "upload_url" in data
        assert "upload_id" in data
        assert "expires_at" in data

        # Verify pending upload was persisted to DB
        mock_pending_queries.create_pending_upload.assert_called_once()


def test_signed_url_gcs_failure_returns_502(client):
    """A GCS error while minting the signed URL surfaces as 502, not a bare 500."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=SAMPLE_BRAND)
        mock_pending_queries.cleanup_expired_uploads = AsyncMock(return_value=0)

        mock_storage = MagicMock()
        mock_storage.generate_signed_upload_url.side_effect = RuntimeError("GCS unavailable")
        mock_storage_fn.return_value = mock_storage

        response = client.post("/api/v1/upload/signed-url", json={
            "filename": "report.csv",
            "content_type": "text/csv",
            "file_type": "cpc_ad_report",
            "brand_id": 123,
        }, headers=AUTH_HEADERS)

        assert response.status_code == 502
        assert response.json()["code"] == "UPLOAD_SIGNED_URL_FAILED"
        # The pending row must not be persisted when the URL never minted.
        mock_pending_queries.create_pending_upload.assert_not_called()


def test_signed_url_invalid_file_type(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        response = client.post("/api/v1/upload/signed-url", json={
            "filename": "file.txt",
            "content_type": "text/plain",
            "file_type": "invalid_type",
            "brand_id": 123,
        }, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["code"] == "UPLOAD_INVALID_FORMAT"


def test_signed_url_brand_not_found(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_svc_conn.fetchrow = AsyncMock(return_value=None)

        mock_pending_queries.cleanup_expired_uploads = AsyncMock(return_value=0)

        response = client.post("/api/v1/upload/signed-url", json={
            "filename": "report.csv",
            "content_type": "text/csv",
            "file_type": "cpc_ad_report",
            "brand_id": 999,
        }, headers=AUTH_HEADERS)

        assert response.status_code == 404
        assert response.json()["code"] == "BRAND_NOT_FOUND"


# ---------------------------------------------------------------------------
# POST /api/v1/upload/process
# ---------------------------------------------------------------------------

def _shopee_csv(header_line: str, data_lines: list[str] | None = None) -> bytes:
    """Build a Shopee-style CSV with 7 metadata rows before the real headers."""
    metadata = [
        "Semua Laporan Iklan CPC - Shopee Indonesia",
        "Username,testuser",
        "Nama Toko,Test Store",
        "ID Toko,123456",
        "Waktu Laporan Dibuat,01/01/2026 00:00",
        "Periode,01/01/2026 - 31/01/2026",
        "",
    ]
    lines = metadata + [header_line] + (data_lines or [])
    return "\n".join(lines).encode()


def _make_csv_bytes():
    """Create valid CPC Ad Report CSV in Shopee format."""
    cols = [
        "Nama Iklan", "Jenis Iklan", "Kode Produk",
        "Penempatan Iklan", "Biaya",
    ]
    return _shopee_csv(",".join(cols), [",".join(["val"] * len(cols))])


def test_process_valid_csv(client):
    """Test processing a valid CSV upload with auto-calculated results."""
    upload_id = "test-uuid-1234"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
        patch("app.modules.upload.service.brand_queries") as mock_brand_queries,
        patch("app.modules.upload.service.upload_queries") as mock_upload_queries,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
        patch("app.modules.upload.service.clear_dependent_results") as mock_clear,
        patch("app.modules.upload.service.run_calculators_for_upload") as mock_run,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Atomic claim returns the pending upload
        mock_pending_queries.claim_pending_upload = AsyncMock(return_value=SAMPLE_PENDING)

        # Brand mock for filename prefix
        mock_brand_queries.get_brand_by_id = AsyncMock(return_value={"id": 123, "brand_name": "TestBrand"})

        # Lightweight storage path check (no existing file to delete)
        mock_upload_queries.get_storage_path_by_type = AsyncMock(return_value=None)
        # Upsert returns the stored upload row
        mock_upload_queries.upsert_upload = AsyncMock(return_value=SAMPLE_UPLOAD)

        # Storage mock
        mock_storage = MagicMock()
        mock_storage.download_file.return_value = _make_csv_bytes()
        mock_storage.delete_file.return_value = None
        mock_storage_fn.return_value = mock_storage

        # DB mock with transaction support
        mock_svc_conn = _make_transactional_conn()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # Engine mocks
        mock_clear.return_value = 0
        mock_run.return_value = [
            {"calculator_type": "ads_keyword", "status": "skipped", "reason": "Missing required files: keyword_report"},
        ]

        response = client.post("/api/v1/upload/process", json={
            "upload_id": upload_id,
            "brand_id": 123,
            "file_type": "cpc_ad_report",
        }, headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["upload"]["brand_id"] == 123
        assert data["upload"]["file_type"] == "cpc_ad_report"
        assert data["upload"]["row_count"] == 50
        assert len(data["auto_calculated"]) == 1
        assert data["auto_calculated"][0]["status"] == "skipped"

        # Verify atomic claim was used (not get + delete)
        mock_pending_queries.claim_pending_upload.assert_called_once()

        # Verify filename was prefixed with brand name before upsert
        upsert_call = mock_upload_queries.upsert_upload.call_args
        assert upsert_call.kwargs["filename"] == "TestBrand_report.csv"

        # File should NOT be deleted after processing (kept for download)
        mock_storage.delete_file.assert_not_called()

        # storage_path should be passed to upsert
        assert upsert_call.kwargs["storage_path"] == f"uploads/{upload_id}/report.csv"


def test_process_missing_columns(client):
    """Test processing a CSV with missing required columns."""
    upload_id = "test-uuid-missing-cols"

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
        patch("app.modules.upload.service.brand_queries") as mock_brand_queries,
        patch("app.modules.upload.service.upload_queries") as mock_upload_queries,
        patch("app.modules.upload.service.get_storage_client") as mock_storage_fn,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Atomic claim returns the pending upload
        mock_pending_queries.claim_pending_upload = AsyncMock(return_value={
            **SAMPLE_PENDING,
            "upload_id": upload_id,
            "filename": "bad_report.csv",
            "object_name": f"uploads/{upload_id}/bad_report.csv",
        })

        # Brand mock for filename prefix
        mock_brand_queries.get_brand_by_id = AsyncMock(return_value={"id": 123, "brand_name": "TestBrand"})
        mock_upload_queries.get_storage_path_by_type = AsyncMock(return_value=None)
        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # CSV with wrong columns (still needs Shopee metadata rows)
        mock_storage = MagicMock()
        mock_storage.download_file.return_value = _shopee_csv(
            "wrong_col_a,wrong_col_b", ["1,2"]
        )
        mock_storage_fn.return_value = mock_storage

        response = client.post("/api/v1/upload/process", json={
            "upload_id": upload_id,
            "brand_id": 123,
            "file_type": "cpc_ad_report",
        }, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["code"] == "UPLOAD_MISSING_COLUMNS"


def test_expired_error_when_upload_expired(client):
    """Test processing with expired upload ID — SQL filters expired rows."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # claim returns None — expired rows are filtered by SQL WHERE expires_at > NOW()
        mock_pending_queries.claim_pending_upload = AsyncMock(return_value=None)

        response = client.post("/api/v1/upload/process", json={
            "upload_id": "test-uuid-expired",
            "brand_id": 123,
            "file_type": "cpc_ad_report",
        }, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["code"] == "UPLOAD_SIGNED_URL_EXPIRED"


def test_expired_error_when_upload_id_unknown(client):
    """Test processing with unknown upload ID."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # claim returns None — upload_id not found
        mock_pending_queries.claim_pending_upload = AsyncMock(return_value=None)

        response = client.post("/api/v1/upload/process", json={
            "upload_id": "nonexistent-id",
            "brand_id": 123,
            "file_type": "cpc_ad_report",
        }, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["code"] == "UPLOAD_SIGNED_URL_EXPIRED"


def test_expired_error_when_upload_already_claimed(client):
    """Test that a second concurrent process_upload fails after the first claims the row."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.pending_queries") as mock_pending_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn

        # claim returns None — row already claimed by another instance
        mock_pending_queries.claim_pending_upload = AsyncMock(return_value=None)

        response = client.post("/api/v1/upload/process", json={
            "upload_id": "already-claimed-uuid",
            "brand_id": 123,
            "file_type": "cpc_ad_report",
        }, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["code"] == "UPLOAD_SIGNED_URL_EXPIRED"


# ---------------------------------------------------------------------------
# GET /api/v1/upload/brands/{brand_id}
# ---------------------------------------------------------------------------

def test_get_uploads_empty(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.brand_queries") as mock_brand_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_brand_queries.get_brand_by_id = AsyncMock(return_value=SAMPLE_BRAND)
        mock_svc_conn.fetch = AsyncMock(return_value=[])

        response = client.get("/api/v1/upload/brands/123", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 123
        assert data["uploads"] == []


def test_get_uploads_with_data(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.brand_queries") as mock_brand_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_brand_queries.get_brand_by_id = AsyncMock(return_value=SAMPLE_BRAND)
        mock_svc_conn.fetch = AsyncMock(return_value=[SAMPLE_UPLOAD])

        response = client.get("/api/v1/upload/brands/123", headers=AUTH_HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["brand_id"] == 123
        assert len(data["uploads"]) == 1
        upload = data["uploads"][0]
        assert upload["file_type"] == "cpc_ad_report"
        assert upload["filename"] == "report.csv"
        assert upload["row_count"] == 50


def test_get_uploads_brand_not_found(client):
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.service.db") as mock_svc_db,
        patch("app.modules.upload.service.brand_queries") as mock_brand_queries,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_svc_conn = AsyncMock()
        mock_svc_db.connection.return_value.__aenter__.return_value = mock_svc_conn
        mock_brand_queries.get_brand_by_id = AsyncMock(return_value=None)

        response = client.get("/api/v1/upload/brands/999", headers=AUTH_HEADERS)

        assert response.status_code == 404
        assert response.json()["code"] == "BRAND_NOT_FOUND"
