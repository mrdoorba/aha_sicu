"""Integration tests for calculator API endpoints."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch


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
    "id": 1,
    "brand_name": "Brand ABC",
    "raw_data": {"category": "Electronics"},
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "meeting_raw_data": None,
}

SAMPLE_CPC_UPLOAD = {
    "id": 1,
    "brand_id": 1,
    "file_type": "cpc_ad_report",
    "calculator_target": "ads_keyword",
    "filename": "cpc_report.csv",
    "file_size": 1024,
    "row_count": 5,
    "parsed_data": {
        "columns": ["Nama Iklan", "Status", "Jenis Iklan", "Kode Produk",
                     "Tampilan Iklan", "Mode Bidding", "Penempatan Iklan",
                     "Biaya", "Omzet Penjualan", "Efektifitas Iklan"],
        "data": [
            {
                "Nama Iklan": "Product Ad [1]",
                "Status": "Berjalan",
                "Jenis Iklan": "Iklan Produk",
                "Kode Produk": "123",
                "Tampilan Iklan": "-",
                "Mode Bidding": "GMV Max ROAS",
                "Penempatan Iklan": "Semua Penempatan",
                "Biaya": 10000,
                "Omzet Penjualan": 50000,
                "Efektifitas Iklan": 5.0,
            },
        ],
        "row_count": 1,
    },
    "uploaded_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
}

SAMPLE_KEYWORD_UPLOAD = {
    "id": 2,
    "brand_id": 1,
    "file_type": "keyword_report",
    "calculator_target": "ads_keyword",
    "filename": "keyword_report.csv",
    "file_size": 2048,
    "row_count": 5,
    "parsed_data": {
        "columns": ["Nama Iklan", "Status", "Jenis Iklan", "Kode Produk",
                     "Tampilan Iklan", "Mode Bidding", "Penempatan Iklan",
                     "Kata Pencarian/Penempatan", "Biaya", "Omzet Penjualan",
                     "Efektifitas Iklan"],
        "data": [
            {
                "Nama Iklan": "Product Ad [1]",
                "Status": "Berjalan",
                "Jenis Iklan": "Iklan Produk",
                "Kode Produk": "123",
                "Tampilan Iklan": "-",
                "Mode Bidding": "GMV Max ROAS",
                "Penempatan Iklan": "Semua Penempatan",
                "Kata Pencarian/Penempatan": "Pilih Otomatis",
                "Biaya": 10000,
                "Omzet Penjualan": 50000,
                "Efektifitas Iklan": 5.0,
            },
        ],
        "row_count": 1,
    },
    "uploaded_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
}

SAMPLE_EVAL_INPUTS = {
    "id": 1,
    "brand_id": 1,
    "last_edited_by": 1,
    "category_type": "fashion",
    "manual_data": {
        "products": {"productCount": 80},
    },
    "created_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 2, 5, 10, 0, 0, tzinfo=timezone.utc),
}

SAMPLE_CALC_RESULT = {
    "id": 1,
    "brand_id": 1,
    "calculator_type": "ads_keyword",
    "details": {"ak2": "text", "thresholds": {}},
    "output_text": "combined text",
    "calculated_at": datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
}

SAMPLE_ORDER_UPLOAD = {
    "id": 3,
    "brand_id": 1,
    "file_type": "order_export",
    "calculator_target": "discount",
    "filename": "order_export.xlsx",
    "file_size": 4096,
    "row_count": 3,
    "parsed_data": {
        "columns": ["No. Pesanan", "Nama Produk", "Harga Awal",
                     "Harga Setelah Diskon", "Jumlah",
                     "Voucher Ditanggung Penjual", "Paket Diskon (Diskon dari Penjual)"],
        "data": [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "2",
                "Voucher Ditanggung Penjual": "5.000",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
            {
                "No. Pesanan": "ORD002",
                "Nama Produk": "Product B",
                "Harga Awal": "50.000",
                "Harga Setelah Diskon": "45.000",
                "Jumlah": "3",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
            {
                "No. Pesanan": "ORD003",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ],
        "row_count": 3,
    },
    "uploaded_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
}

SAMPLE_DISCOUNT_RESULT = {
    "id": 2,
    "brand_id": 1,
    "calculator_type": "discount",
    "details": {"discount_pct": "10.0%", "fake_discount_flag": False},
    "output_text": "% Diskon TOP SKU: 10.0%\nRange: 0.0% ~ 0.0%\nVoucher 0.0%\nPaket Diskon 0.0%",
    "calculated_at": datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
}


def _make_transactional_conn(fetchrow_side_effect):
    """Create a mock connection that supports conn.transaction()."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(side_effect=fetchrow_side_effect)

    @asynccontextmanager
    async def mock_transaction():
        yield

    mock_conn.transaction = mock_transaction
    return mock_conn


def _setup_auth_mocks(mock_verify, mock_db, mock_user_queries):
    """Shared auth mock setup for all tests."""
    mock_verify.return_value = {"uid": "test-uid", "email": "test@example.com"}
    mock_conn = AsyncMock()
    mock_db.connection.return_value.__aenter__.return_value = mock_conn
    mock_user_queries.get_user_by_firebase_uid = AsyncMock(return_value=MOCK_USER)
    mock_user_queries.update_last_login = AsyncMock()


def test_run_ads_keyword_calculator_without_token(client):
    """POST calculator endpoint returns 401 without token."""
    response = client.post("/api/v1/evaluations/brands/1/calculators/ads_keyword")
    assert response.status_code == 401


def test_run_ads_keyword_calculator_success(client):
    """POST returns calculator result when all data present."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Service DB: brand → cpc_upload → keyword_upload → eval_inputs → upsert
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,           # get_brand_by_id
            SAMPLE_CPC_UPLOAD,      # get_upload_by_type (cpc_ad_report)
            SAMPLE_KEYWORD_UPLOAD,  # get_upload_by_type (keyword_report)
            SAMPLE_EVAL_INPUTS,     # get_evaluation_inputs
            SAMPLE_CALC_RESULT,     # upsert_result
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["calculator_type"] == "ads_keyword"
        assert "output_text" in data
        assert "details" in data
        assert "calculated_at" in data


def test_run_ads_keyword_missing_cpc_report(client):
    """POST returns 400 when CPC Ad Report not uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,  # get_brand_by_id
            None,          # get_upload_by_type (cpc_ad_report) → missing
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "cpc_ad_report" in data["detail"]


def test_run_ads_keyword_missing_keyword_report(client):
    """POST returns 400 when Keyword Report not uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,           # get_brand_by_id
            SAMPLE_CPC_UPLOAD,      # get_upload_by_type (cpc_ad_report)
            None,                   # get_upload_by_type (keyword_report) → missing
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "keyword_report" in data["detail"]


def test_run_ads_keyword_missing_total_products(client):
    """POST returns 400 when total_products not set in manual data."""
    eval_inputs_no_products = {
        **SAMPLE_EVAL_INPUTS,
        "manual_data": {"someOtherData": "value"},
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,               # get_brand_by_id
            SAMPLE_CPC_UPLOAD,           # cpc_ad_report
            SAMPLE_KEYWORD_UPLOAD,       # keyword_report
            eval_inputs_no_products,     # eval_inputs without products
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "productCount" in data["detail"]


def test_run_ads_keyword_upsert_on_recalculation(client):
    """Running calculator twice should update (upsert) existing result."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # First run
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_CPC_UPLOAD, SAMPLE_KEYWORD_UPLOAD,
            SAMPLE_EVAL_INPUTS, SAMPLE_CALC_RESULT,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        resp1 = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )
        assert resp1.status_code == 200

        # Second run (same data, should upsert)
        updated_result = {
            **SAMPLE_CALC_RESULT,
            "calculated_at": datetime(2026, 2, 11, 11, 0, 0, tzinfo=timezone.utc),
        }
        mock_calc_conn2 = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_CPC_UPLOAD, SAMPLE_KEYWORD_UPLOAD,
            SAMPLE_EVAL_INPUTS, updated_result,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn2

        resp2 = client.post(
            "/api/v1/evaluations/brands/1/calculators/ads_keyword",
            headers=AUTH_HEADERS,
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["calculator_type"] == "ads_keyword"


# ---------------------------------------------------------------------------
# Discount Calculator integration tests
# ---------------------------------------------------------------------------


def test_run_discount_calculator_without_token(client):
    """POST discount calculator returns 401 without token."""
    response = client.post("/api/v1/evaluations/brands/1/calculators/discount")
    assert response.status_code == 401


def test_run_discount_calculator_success(client):
    """POST returns calculator result when order_export present."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Service DB: brand → order_upload → upsert
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,           # get_brand_by_id
            SAMPLE_ORDER_UPLOAD,    # get_upload_by_type (order_export)
            SAMPLE_DISCOUNT_RESULT, # upsert_result
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["calculator_type"] == "discount"
        assert "output_text" in data
        assert "details" in data
        assert "calculated_at" in data


def test_run_discount_missing_order_export(client):
    """POST returns 400 when order_export not uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,  # get_brand_by_id
            None,          # get_upload_by_type (order_export) → missing
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "order_export" in data["detail"]


def test_run_discount_upsert_on_recalculation(client):
    """Running discount calculator twice should upsert existing result."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # First run
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_ORDER_UPLOAD, SAMPLE_DISCOUNT_RESULT,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        resp1 = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )
        assert resp1.status_code == 200

        # Second run (upsert)
        updated_result = {
            **SAMPLE_DISCOUNT_RESULT,
            "calculated_at": datetime(2026, 2, 11, 11, 0, 0, tzinfo=timezone.utc),
        }
        mock_calc_conn2 = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_ORDER_UPLOAD, updated_result,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn2

        resp2 = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["calculator_type"] == "discount"


SAMPLE_ORDER_UPLOAD_TOP_SKU = {
    "id": 4,
    "brand_id": 1,
    "file_type": "order_export",
    "calculator_target": "top_sku",
    "filename": "order_export.xlsx",
    "file_size": 4096,
    "row_count": 2,
    "parsed_data": {
        "columns": [
            "No. Pesanan", "Nama Produk", "Nomor Referensi SKU",
            "Nama Variasi", "Harga Setelah Diskon", "Jumlah",
            "Jumlah Produk di Pesan", "Voucher Ditanggung Penjual",
            "Cashback Koin", "Diskon Dari Shopee",
            "Harga Awal", "Paket Diskon (Diskon dari Penjual)",
        ],
        "data": [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Nomor Referensi SKU": "SKU001",
                "Nama Variasi": "Red",
                "Harga Setelah Diskon": "100.000",
                "Jumlah": 2,
                "Jumlah Produk di Pesan": 2,
                "Voucher Ditanggung Penjual": "0",
                "Cashback Koin": "0",
                "Diskon Dari Shopee": "0",
                "Harga Awal": "120.000",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
            {
                "No. Pesanan": "ORD002",
                "Nama Produk": "Product B",
                "Nomor Referensi SKU": "SKU002",
                "Nama Variasi": "Blue",
                "Harga Setelah Diskon": "200.000",
                "Jumlah": 1,
                "Jumlah Produk di Pesan": 1,
                "Voucher Ditanggung Penjual": "0",
                "Cashback Koin": "0",
                "Diskon Dari Shopee": "0",
                "Harga Awal": "250.000",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ],
        "row_count": 2,
    },
    "uploaded_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
}

SAMPLE_MASS_UPDATE_UPLOAD = {
    "id": 5,
    "brand_id": 1,
    "file_type": "mass_update",
    "calculator_target": "top_sku",
    "filename": "mass_update.xlsx",
    "file_size": 2048,
    "row_count": 2,
    "parsed_data": {
        "columns": ["Nama Produk", "Nama Variasi", "Kode Variasi", "Stok"],
        "data": [
            {"Nama Produk": "Product A", "Nama Variasi": "Red", "Kode Variasi": "K001", "Stok": 100},
            {"Nama Produk": "Product B", "Nama Variasi": "Blue", "Kode Variasi": "K002", "Stok": 50},
        ],
        "row_count": 2,
    },
    "uploaded_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
}

SAMPLE_TOP_SKU_RESULT = {
    "id": 3,
    "brand_id": 1,
    "calculator_type": "top_sku",
    "details": {"output_1": [], "output_2": [], "average_stock": 75, "product_count": 2, "total_unique_products": 2},
    "output_text": "",
    "calculated_at": datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
}


def test_run_discount_missing_columns(client):
    """POST returns 400 when order_export is missing required columns."""
    upload_missing_cols = {
        **SAMPLE_ORDER_UPLOAD,
        "parsed_data": {
            "columns": ["No. Pesanan", "Nama Produk"],  # Missing 5 required columns
            "data": [{"No. Pesanan": "ORD001", "Nama Produk": "Product A"}],
            "row_count": 1,
        },
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,           # get_brand_by_id
            upload_missing_cols,    # get_upload_by_type (order_export)
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "missing required columns" in data["detail"]
        # Verify specific missing columns are listed
        assert "Harga Awal" in data["detail"]
        assert "Jumlah" in data["detail"]


def test_run_discount_string_parsed_data(client):
    """POST succeeds when parsed_data is a JSON string (double-encoded legacy data)."""
    import json

    upload_string_parsed = {
        **SAMPLE_ORDER_UPLOAD,
        "parsed_data": json.dumps(SAMPLE_ORDER_UPLOAD["parsed_data"]),
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,               # get_brand_by_id
            upload_string_parsed,       # get_upload_by_type (order_export) — string parsed_data
            SAMPLE_DISCOUNT_RESULT,     # upsert_result
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/discount",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["calculator_type"] == "discount"


# ---------------------------------------------------------------------------
# Top SKU Calculator integration tests
# ---------------------------------------------------------------------------


def test_run_top_sku_calculator_without_token(client):
    """POST top_sku calculator returns 401 without token."""
    response = client.post("/api/v1/evaluations/brands/1/calculators/top_sku")
    assert response.status_code == 401


def test_run_top_sku_calculator_success(client):
    """POST returns calculator result when both order_export and mass_update present."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Service DB: brand → order_upload → mass_update_upload → upsert
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,                 # get_brand_by_id
            SAMPLE_ORDER_UPLOAD_TOP_SKU,  # get_upload_by_type (order_export)
            SAMPLE_MASS_UPDATE_UPLOAD,    # get_upload_by_type (mass_update)
            SAMPLE_TOP_SKU_RESULT,        # upsert_result
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["calculator_type"] == "top_sku"
        assert "output_text" in data
        assert "details" in data
        assert "calculated_at" in data


def test_run_top_sku_missing_order_export(client):
    """POST returns 400 when order_export not uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,  # get_brand_by_id
            None,          # get_upload_by_type (order_export) → missing
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "order_export" in data["detail"]


def test_run_top_sku_missing_mass_update(client):
    """POST returns 400 when mass_update not uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,                 # get_brand_by_id
            SAMPLE_ORDER_UPLOAD_TOP_SKU,  # get_upload_by_type (order_export)
            None,                         # get_upload_by_type (mass_update) → missing
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "mass_update" in data["detail"]


def test_run_top_sku_missing_columns(client):
    """POST returns 400 when mass_update is missing required columns."""
    upload_missing_cols = {
        **SAMPLE_MASS_UPDATE_UPLOAD,
        "parsed_data": {
            "columns": ["Nama Produk"],  # Missing Nama Variasi, Kode Variasi, Stok
            "data": [{"Nama Produk": "Product A"}],
            "row_count": 1,
        },
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,                 # get_brand_by_id
            SAMPLE_ORDER_UPLOAD_TOP_SKU,  # get_upload_by_type (order_export)
            upload_missing_cols,          # get_upload_by_type (mass_update)
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "missing required columns" in data["detail"]


def test_run_top_sku_missing_order_export_columns(client):
    """POST returns 400 when order_export is missing top_sku-specific columns."""
    upload_missing_cols = {
        **SAMPLE_ORDER_UPLOAD_TOP_SKU,
        "parsed_data": {
            "columns": ["No. Pesanan", "Nama Produk", "Jumlah"],  # Missing top_sku columns
            "data": [{"No. Pesanan": "ORD001", "Nama Produk": "Product A", "Jumlah": 1}],
            "row_count": 1,
        },
    }

    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND,           # get_brand_by_id
            upload_missing_cols,    # get_upload_by_type (order_export)
            SAMPLE_MASS_UPDATE_UPLOAD,  # get_upload_by_type (mass_update)
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "CALC_MISSING_DATA"
        assert "missing required columns" in data["detail"]
        assert "Cashback Koin" in data["detail"]


def test_run_top_sku_upsert_on_recalculation(client):
    """Running top_sku calculator twice should upsert existing result."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.calculator_service.db") as mock_calc_db,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # First run
        mock_calc_conn = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_ORDER_UPLOAD_TOP_SKU,
            SAMPLE_MASS_UPDATE_UPLOAD, SAMPLE_TOP_SKU_RESULT,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn

        resp1 = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )
        assert resp1.status_code == 200

        # Second run (upsert)
        updated_result = {
            **SAMPLE_TOP_SKU_RESULT,
            "calculated_at": datetime(2026, 2, 11, 11, 0, 0, tzinfo=timezone.utc),
        }
        mock_calc_conn2 = _make_transactional_conn([
            SAMPLE_BRAND, SAMPLE_ORDER_UPLOAD_TOP_SKU,
            SAMPLE_MASS_UPDATE_UPLOAD, updated_result,
        ])
        mock_calc_db.connection.return_value.__aenter__.return_value = mock_calc_conn2

        resp2 = client.post(
            "/api/v1/evaluations/brands/1/calculators/top_sku",
            headers=AUTH_HEADERS,
        )
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["calculator_type"] == "top_sku"


# ---------------------------------------------------------------------------
# Calculator Orchestration: run-all endpoint integration tests
# ---------------------------------------------------------------------------


def test_run_all_auth_required(client):
    """POST run-all returns 401 without token."""
    response = client.post("/api/v1/evaluations/brands/1/calculators/run-all")
    assert response.status_code == 401


def test_run_all_returns_ready_calculator_results(client):
    """POST run-all returns results for ready calculators, skips pending."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.run_ready_calculators") as mock_run,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_run.return_value = [
            {
                "calculator_type": "discount",
                "status": "success",
                "result": {
                    "calculator_type": "discount",
                    "output_text": "test",
                    "details": {},
                    "calculated_at": "2026-02-11T10:00:00+00:00",
                },
            },
            {
                "calculator_type": "top_sku",
                "status": "skipped",
                "reason": "Missing required files: mass_update",
            },
        ]

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/run-all",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2

    discount_r = next(r for r in data["results"] if r["calculator_type"] == "discount")
    top_sku_r = next(r for r in data["results"] if r["calculator_type"] == "top_sku")

    assert discount_r["status"] == "success"
    assert discount_r["result"]["calculator_type"] == "discount"
    assert top_sku_r["status"] == "skipped"
    assert "mass_update" in top_sku_r["reason"]


def test_run_all_skips_calculators_missing_files(client):
    """POST run-all skips all calculators when no files uploaded."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.run_ready_calculators") as mock_run,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_run.return_value = [
            {"calculator_type": "ads_keyword", "status": "skipped", "reason": "Missing required files: cpc_ad_report, keyword_report"},
            {"calculator_type": "discount", "status": "skipped", "reason": "Missing required files: order_export"},
            {"calculator_type": "top_sku", "status": "skipped", "reason": "Missing required files: order_export, mass_update"},
        ]

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/run-all",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert all(r["status"] == "skipped" for r in data["results"])


def test_run_all_isolates_failures(client):
    """POST run-all returns error for failed calculator, success for others."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.run_ready_calculators") as mock_run,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_run.return_value = [
            {"calculator_type": "discount", "status": "error", "reason": "Calculator execution failed"},
            {
                "calculator_type": "top_sku",
                "status": "success",
                "result": {
                    "calculator_type": "top_sku",
                    "output_text": "",
                    "details": {},
                    "calculated_at": "2026-02-11T10:00:00+00:00",
                },
            },
        ]

        response = client.post(
            "/api/v1/evaluations/brands/1/calculators/run-all",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    statuses = {r["calculator_type"]: r["status"] for r in data["results"]}
    assert statuses["discount"] == "error"
    assert statuses["top_sku"] == "success"


# ---------------------------------------------------------------------------
# Calculator Orchestration: status endpoint integration tests
# ---------------------------------------------------------------------------


def test_calculator_status_auth_required(client):
    """GET calculator status returns 401 without token."""
    response = client.get("/api/v1/evaluations/brands/1/calculators/status")
    assert response.status_code == 401


def test_calculator_status_correct_readiness(client):
    """GET status returns correct readiness per calculator."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.check_calculator_readiness") as mock_check,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_check.return_value = {
            "ads_keyword": {
                "status": "pending",
                "has_result": False,
                "required_files": ["cpc_ad_report", "keyword_report"],
                "required_manual": ["total_products"],
                "available_files": ["cpc_ad_report"],
                "missing_files": ["keyword_report"],
                "missing_manual": ["total_products"],
                "calculated_at": None,
            },
            "discount": {
                "status": "ready",
                "has_result": True,
                "required_files": ["order_export"],
                "required_manual": [],
                "available_files": ["order_export"],
                "missing_files": [],
                "missing_manual": [],
                "calculated_at": "2026-02-11T10:30:00+00:00",
            },
            "top_sku": {
                "status": "ready",
                "has_result": True,
                "required_files": ["order_export", "mass_update"],
                "required_manual": [],
                "available_files": ["order_export", "mass_update"],
                "missing_files": [],
                "missing_manual": [],
                "calculated_at": "2026-02-11T10:31:00+00:00",
            },
        }

        response = client.get(
            "/api/v1/evaluations/brands/1/calculators/status",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_id"] == 1

    ads = data["calculators"]["ads_keyword"]
    assert ads["status"] == "pending"
    assert ads["has_result"] is False
    assert "keyword_report" in ads["missing_files"]
    assert "total_products" in ads["missing_manual"]

    disc = data["calculators"]["discount"]
    assert disc["status"] == "ready"
    assert disc["has_result"] is True
    assert disc["calculated_at"] is not None

    top = data["calculators"]["top_sku"]
    assert top["status"] == "ready"
    assert top["has_result"] is True


def test_calculator_status_reflects_existing_results(client):
    """GET status has_result=True and calculated_at when results exist."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.check_calculator_readiness") as mock_check,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_check.return_value = {
            "discount": {
                "status": "ready",
                "has_result": True,
                "required_files": ["order_export"],
                "required_manual": [],
                "available_files": ["order_export"],
                "missing_files": [],
                "missing_manual": [],
                "calculated_at": "2026-02-11T10:30:00+00:00",
            },
        }

        response = client.get(
            "/api/v1/evaluations/brands/1/calculators/status",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["calculators"]["discount"]["has_result"] is True
    assert data["calculators"]["discount"]["calculated_at"] is not None


# ---------------------------------------------------------------------------
# Upload auto-execute integration tests
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GET calculator results endpoint integration tests
# ---------------------------------------------------------------------------


def test_get_calculator_results_auth_required(client):
    """GET calculator results returns 401 without token."""
    response = client.get("/api/v1/evaluations/brands/1/calculators/results")
    assert response.status_code == 401


def test_get_calculator_results_returns_all_results(client):
    """GET returns all stored calculator results for a brand."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.calc_queries.get_results_by_brand") as mock_get_results,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_get_results.return_value = [
            {
                "id": 1,
                "brand_id": 1,
                "calculator_type": "ads_keyword",
                "output_text": "34 dari 80 produk (42.5%) sudah beriklan",
                "details": {"ak2": "text", "thresholds": {}},
                "calculated_at": datetime(2026, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "brand_id": 1,
                "calculator_type": "discount",
                "output_text": "% Diskon TOP SKU: 2.7%",
                "details": {"discount_pct": "2.7%", "fake_discount_flag": False},
                "calculated_at": datetime(2026, 2, 11, 10, 30, 0, tzinfo=timezone.utc),
            },
        ]

        response = client.get(
            "/api/v1/evaluations/brands/1/calculators/results",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_id"] == 1
    assert len(data["results"]) == 2

    ads = next(r for r in data["results"] if r["calculator_type"] == "ads_keyword")
    assert ads["output_text"] == "34 dari 80 produk (42.5%) sudah beriklan"
    assert "details" in ads
    assert "calculated_at" in ads

    disc = next(r for r in data["results"] if r["calculator_type"] == "discount")
    assert disc["output_text"] == "% Diskon TOP SKU: 2.7%"


def test_get_calculator_results_empty_when_none(client):
    """GET returns empty results list when no calculator results exist."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.evaluations.service.db") as mock_router_db,
        patch("app.modules.evaluations.service.calc_queries.get_results_by_brand") as mock_get_results,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        mock_conn = AsyncMock()
        mock_router_db.connection.return_value.__aenter__.return_value = mock_conn

        mock_get_results.return_value = []

        response = client.get(
            "/api/v1/evaluations/brands/1/calculators/results",
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["brand_id"] == 1
    assert data["results"] == []


def test_upload_reupload_clears_and_reruns(client):
    """Re-uploading a file clears dependent results and re-runs calculators."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.router.process_upload") as mock_process,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        from app.modules.upload.schemas import (
            AutoCalculatedItem,
            ProcessUploadResponse,
            UploadResponse,
        )

        # Simulate re-upload of order_export: clears discount+top_sku, re-runs discount
        mock_process.return_value = ProcessUploadResponse(
            upload=UploadResponse(
                id=2,
                brand_id=1,
                file_type="order_export",
                filename="order_v2.xlsx",
                file_size=8192,
                row_count=200,
                uploaded_at=datetime(2026, 2, 11, 12, 0, tzinfo=timezone.utc),
            ),
            auto_calculated=[
                AutoCalculatedItem(
                    calculator_type="discount",
                    status="success",
                    result={
                        "calculator_type": "discount",
                        "output_text": "re-calculated",
                        "details": {"discount_pct": "15.0%"},
                        "calculated_at": "2026-02-11T12:00:00+00:00",
                    },
                ),
                AutoCalculatedItem(
                    calculator_type="top_sku",
                    status="skipped",
                    reason="Missing required files: mass_update",
                ),
            ],
        )

        response = client.post(
            "/api/v1/upload/process",
            json={"upload_id": "reupload-id", "brand_id": 1, "file_type": "order_export"},
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()

    # Upload reflects the new file
    assert data["upload"]["id"] == 2
    assert data["upload"]["row_count"] == 200
    assert data["upload"]["filename"] == "order_v2.xlsx"

    # Auto-calculated shows re-run results
    assert len(data["auto_calculated"]) == 2
    discount_r = next(r for r in data["auto_calculated"] if r["calculator_type"] == "discount")
    top_sku_r = next(r for r in data["auto_calculated"] if r["calculator_type"] == "top_sku")
    assert discount_r["status"] == "success"
    assert discount_r["result"]["output_text"] == "re-calculated"
    assert top_sku_r["status"] == "skipped"


def test_upload_process_includes_auto_calculated(client):
    """POST upload process response includes auto_calculated results."""
    with (
        patch("app.core.dependencies.verify_firebase_token") as mock_verify,
        patch("app.core.dependencies.db") as mock_db,
        patch("app.core.dependencies.user_queries") as mock_user_queries,
        patch("app.modules.upload.router.process_upload") as mock_process,
    ):
        _setup_auth_mocks(mock_verify, mock_db, mock_user_queries)

        # Mock the full ProcessUploadResponse
        from app.modules.upload.schemas import (
            AutoCalculatedItem,
            ProcessUploadResponse,
            UploadResponse,
        )

        mock_process.return_value = ProcessUploadResponse(
            upload=UploadResponse(
                id=1,
                brand_id=1,
                file_type="order_export",
                filename="order.xlsx",
                file_size=4096,
                row_count=100,
                uploaded_at=datetime(2026, 2, 11, 10, 0, tzinfo=timezone.utc),
            ),
            auto_calculated=[
                AutoCalculatedItem(
                    calculator_type="discount",
                    status="success",
                    result={
                        "calculator_type": "discount",
                        "output_text": "test",
                        "details": {},
                        "calculated_at": "2026-02-11T10:00:00+00:00",
                    },
                ),
                AutoCalculatedItem(
                    calculator_type="top_sku",
                    status="skipped",
                    reason="Missing required files: mass_update",
                ),
            ],
        )

        response = client.post(
            "/api/v1/upload/process",
            json={"upload_id": "test-id", "brand_id": 1, "file_type": "order_export"},
            headers=AUTH_HEADERS,
        )

    assert response.status_code == 200
    data = response.json()

    # Verify upload field present
    assert data["upload"]["id"] == 1
    assert data["upload"]["file_type"] == "order_export"

    # Verify auto_calculated field
    assert len(data["auto_calculated"]) == 2
    discount_r = next(r for r in data["auto_calculated"] if r["calculator_type"] == "discount")
    top_sku_r = next(r for r in data["auto_calculated"] if r["calculator_type"] == "top_sku")
    assert discount_r["status"] == "success"
    assert top_sku_r["status"] == "skipped"
