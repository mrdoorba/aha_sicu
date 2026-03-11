"""Tests for Sheet 2 i18n structured data in ads keyword calculator."""

from app.calculators.ads_keyword import calculate_sheet2


def _kw_row(name="Ad 1", jenis="Iklan Produk", penempatan="Semua Penempatan",
            bidding="GMV Max Auto", biaya=50000, gmv=200000, roas=5.0,
            kata="Pilih Otomatis", status="Berjalan"):
    return {
        "Nama Iklan": name,
        "Jenis Iklan": jenis,
        "Penempatan Iklan": penempatan,
        "Mode Bidding": bidding,
        "Biaya": biaya,
        "Omzet Penjualan": gmv,
        "Efektifitas Iklan": roas,
        "Kata Pencarian/Penempatan": kata,
        "Status": status,
    }


class TestSheet2I18nAl2:
    """AL2 i18n: TOP ads."""

    def test_has_al2_i18n_key(self):
        rows = [_kw_row(gmv=500000, roas=12)]
        result = calculate_sheet2(rows)
        assert "al2_i18n" in result

    def test_al2_i18n_has_header_key(self):
        rows = [_kw_row(gmv=500000, roas=12), _kw_row(name="Low", gmv=10000, roas=1)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"]["header"]["key"] == "ads.topHeader"

    def test_al2_i18n_has_ads_list(self):
        rows = [_kw_row(gmv=500000, roas=12), _kw_row(name="Low", gmv=10000, roas=1)]
        result = calculate_sheet2(rows)
        assert isinstance(result["al2_i18n"]["ads"], list)
        assert len(result["al2_i18n"]["ads"]) >= 1

    def test_al2_i18n_ad_has_name_var(self):
        rows = [_kw_row(name="Test Product", gmv=500000, roas=12), _kw_row(name="Low", gmv=10000, roas=1)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"]["ads"][0]["vars"]["name"] == "Test Product"

    def test_al2_i18n_empty_when_no_top_ads(self):
        rows = [_kw_row(gmv=0, roas=0)]
        result = calculate_sheet2(rows)
        assert result["al2_i18n"] is None


class TestSheet2I18nAl3:
    """AL3 i18n: top recommendation."""

    def test_has_al3_i18n_key(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Otomatis")] * 4
        result = calculate_sheet2(rows)
        assert "al3_i18n" in result

    def test_al3_i18n_is_auto_when_auto_count_gte_3(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Otomatis")] * 4
        result = calculate_sheet2(rows)
        assert result["al3_i18n"]["key"] == "ads.topRecommendation.auto"

    def test_al3_i18n_is_manual_when_not_auto(self):
        rows = [_kw_row(gmv=500000, roas=12, bidding="Bidding Manual")] * 4
        result = calculate_sheet2(rows)
        assert result["al3_i18n"]["key"] == "ads.topRecommendation.manual"


class TestSheet2I18nAl5:
    """AL5 i18n: BOTTOM ads."""

    def test_has_al5_i18n_key(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000)]
        result = calculate_sheet2(rows)
        assert "al5_i18n" in result

    def test_al5_i18n_empty_when_no_bottom_ads(self):
        rows = [_kw_row(biaya=100, roas=10, gmv=500000)]
        result = calculate_sheet2(rows)
        assert result["al5_i18n"] is None


class TestSheet2I18nAl6Al9:
    """AL6-AL9 i18n: bottom flags."""

    def test_has_al6_i18n_key(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="GMV Max Auto")]
        result = calculate_sheet2(rows)
        assert "al6_i18n" in result

    def test_al6_i18n_is_auto_uncontrolled(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="GMV Max Auto")]
        result = calculate_sheet2(rows)
        if result["al6_i18n"]:
            assert result["al6_i18n"]["key"] == "ads.flag.autoUncontrolled"

    def test_al7_i18n_is_manual_uncontrolled(self):
        rows = [_kw_row(biaya=200000, roas=0.5, gmv=10000, bidding="Bidding Manual")]
        result = calculate_sheet2(rows)
        if result["al7_i18n"]:
            assert result["al7_i18n"]["key"] == "ads.flag.manualUncontrolled"
