"""Tests for i18n structured data in ads keyword calculator."""

from app.calculators.ads_keyword import calculate_sheet1


class TestSheet1I18nAk2:
    """AK2 i18n: ad overview summary."""

    def test_has_ak2_i18n_key_when_rows_provided(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert "ak2_i18n" in result

    def test_ak2_i18n_key_is_ads_summary(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["key"] == "ads.summary"

    def test_ak2_i18n_vars_has_active_count(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
            {"Status": "Dijeda", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 2",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["vars"]["active"] == "1"

    def test_ak2_i18n_vars_has_paused_count(self):
        rows = [
            {"Status": "Dijeda", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["vars"]["paused"] == "1"

    def test_ak2_i18n_vars_has_ended_count(self):
        rows = [
            {"Status": "Berakhir", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["vars"]["ended"] == "1"

    def test_ak2_i18n_vars_has_unique_count(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 2",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["vars"]["unique_count"] == "2"

    def test_ak2_i18n_vars_has_product_pct(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak2_i18n"]["vars"]["product_pct"] == "10.0%"

    def test_ak2_i18n_vars_has_total_products(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 50)
        assert result["ak2_i18n"]["vars"]["total_products"] == "50"


class TestSheet1I18nAk3:
    """AK3 i18n: ad type breakdown."""

    def test_has_ak3_i18n_key_when_rows_provided(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert "ak3_i18n" in result

    def test_ak3_i18n_key_is_ads_type_breakdown(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak3_i18n"]["key"] == "ads.typeBreakdown"

    def test_ak3_i18n_vars_has_semua_total(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak3_i18n"]["vars"]["semua_total"] == "1"

    def test_ak3_i18n_vars_has_toko_counts(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Toko", "Nama Iklan": "Shop Ad",
             "Penempatan Iklan": "Halaman Pencarian", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak3_i18n"]["vars"]["toko_total"] == "1"
        assert result["ak3_i18n"]["vars"]["toko_auto"] == "1"
        assert result["ak3_i18n"]["vars"]["toko_manual"] == "0"


class TestSheet1I18nAk4:
    """AK4 i18n: recommendation flags."""

    def test_has_ak4_i18n_key_when_rows_provided(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert "ak4_i18n" in result

    def test_ak4_i18n_key_is_ads_recommendations(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak4_i18n"]["key"] == "ads.recommendations"

    def test_ak4_i18n_vars_has_product_pct(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert "product_pct" in result["ak4_i18n"]["vars"]

    def test_ak4_i18n_vars_has_active_ratio(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert "active_ratio" in result["ak4_i18n"]["vars"]

    def test_ak4_i18n_vars_has_has_toko(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Toko", "Nama Iklan": "Shop Ad",
             "Penempatan Iklan": "Halaman Pencarian", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak4_i18n"]["vars"]["has_toko"] == "true"

    def test_ak4_i18n_vars_has_toko_false_when_no_toko_ads(self):
        rows = [
            {"Status": "Berjalan", "Jenis Iklan": "Iklan Produk", "Nama Iklan": "Ad 1",
             "Penempatan Iklan": "Semua Penempatan", "Mode Bidding": "Bidding Otomatis"},
        ]
        result = calculate_sheet1(rows, 10)
        assert result["ak4_i18n"]["vars"]["has_toko"] == "false"
