"""Unit tests for the Top SKU Calculator.

Tests against the spec in logic/calculator-2-penjualan.md
with KYPSO and MND sample data patterns.
"""

import pytest

from app.calculators.top_sku import (
    AggregatedProduct,
    EnrichedProduct,
    LineItem,
    TopSkuResult,
    _aggregate_by_product,
    _build_mass_update_lookup,
    _build_output_tables,
    _calculate_average_stock,
    _clean_price,
    _enrich_with_mass_update,
    _extract_per_line,
    _rank_top_products,
    _safe_num,
    calculate_top_sku,
)


# ---------------------------------------------------------------------------
# _clean_price tests
# ---------------------------------------------------------------------------


class TestCleanPrice:
    def test_removes_dots(self):
        assert _clean_price("529.000") == 529000.0

    def test_multiple_dots(self):
        assert _clean_price("1.250.000") == 1250000.0

    def test_empty_string(self):
        assert _clean_price("") == 0.0

    def test_none(self):
        assert _clean_price(None) == 0.0

    def test_zero_string(self):
        assert _clean_price("0") == 0.0

    def test_integer_passthrough(self):
        assert _clean_price(100000) == 100000.0

    def test_float_passthrough(self):
        assert _clean_price(99.5) == 99.5

    def test_non_numeric_string(self):
        assert _clean_price("abc") == 0.0


# ---------------------------------------------------------------------------
# _safe_num tests
# ---------------------------------------------------------------------------


class TestSafeNum:
    def test_none_returns_zero(self):
        assert _safe_num(None) == 0.0

    def test_integer_input(self):
        assert _safe_num(5) == 5.0

    def test_float_input(self):
        assert _safe_num(3.14) == 3.14

    def test_empty_string(self):
        assert _safe_num("") == 0.0

    def test_dash_string(self):
        assert _safe_num("-") == 0.0

    def test_numeric_string(self):
        assert _safe_num("42") == 42.0

    def test_non_numeric_string(self):
        assert _safe_num("abc") == 0.0


# ---------------------------------------------------------------------------
# _extract_per_line tests
# ---------------------------------------------------------------------------


class TestExtractPerLine:
    def test_revenue_formula_correctness(self):
        """Revenue = (Harga Setelah Diskon × Jumlah)
                   - (Voucher / Jumlah Produk di Pesan)
                   - (Cashback / Jumlah Produk di Pesan)
                   + (Diskon Shopee / Jumlah Produk di Pesan)
        """
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",  # 100000
            "Jumlah": 2,
            "Jumlah Produk di Pesan": 4,
            "Voucher Ditanggung Penjual": "20.000",  # 20000
            "Cashback Koin": "8.000",  # 8000
            "Diskon Dari Shopee": "4.000",  # 4000
        }]
        items = _extract_per_line(rows)
        assert len(items) == 1
        # (100000 * 2) - (20000/4) - (8000/4) + (4000/4)
        # = 200000 - 5000 - 2000 + 1000 = 194000
        assert items[0].revenue == 194000.0

    def test_price_cleaning_before_multiplication(self):
        """Price strings with dots must be cleaned before math."""
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "Product A",
            "Nama Variasi": "Blue",
            "Harga Setelah Diskon": "529.000",  # 529000
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 1,
            "Voucher Ditanggung Penjual": "0",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        items = _extract_per_line(rows)
        assert items[0].revenue == 529000.0

    def test_order_level_discount_splitting(self):
        """Voucher/cashback/Shopee discount divided by Jumlah Produk di Pesan."""
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 2,  # 2 items in order
            "Voucher Ditanggung Penjual": "10.000",  # split: 5000
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        items = _extract_per_line(rows)
        # (100000 * 1) - (10000/2) = 100000 - 5000 = 95000
        assert items[0].revenue == 95000.0

    def test_shopee_discount_added_back(self):
        """Diskon Dari Shopee is ADDED, not subtracted."""
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 1,
            "Voucher Ditanggung Penjual": "0",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "10.000",  # Added back
        }]
        items = _extract_per_line(rows)
        # (100000 * 1) + (10000/1) = 110000
        assert items[0].revenue == 110000.0

    def test_product_variant_label(self):
        """Label = Nama Produk + ' - ' + Nama Variasi."""
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "KYPSO Sovereign",
            "Nama Variasi": "Cokelat Muda",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 1,
            "Voucher Ditanggung Penjual": "0",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        items = _extract_per_line(rows)
        assert items[0].product_variant_label == "KYPSO Sovereign - Cokelat Muda"
        assert items[0].sku == "SKU001"

    def test_zero_jumlah_produk_di_pesan(self):
        """Division by zero protection for Jumlah Produk di Pesan."""
        rows = [{
            "Nomor Referensi SKU": "SKU001",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 0,
            "Voucher Ditanggung Penjual": "10.000",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        items = _extract_per_line(rows)
        # Should not crash; treats as 1
        assert items[0].revenue == 100000.0 - 10000.0


# ---------------------------------------------------------------------------
# _aggregate_by_product tests
# ---------------------------------------------------------------------------


class TestAggregateByProduct:
    def test_groups_by_product_variant_label(self):
        items = [
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=2, revenue=200000),
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=3, revenue=300000),
            LineItem(sku="S2", product_variant_label="Prod B - Blue", quantity=1, revenue=100000),
        ]
        result = _aggregate_by_product(items)
        assert len(result) == 2

    def test_sums_qty_and_revenue(self):
        items = [
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=2, revenue=200000),
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=3, revenue=300000),
        ]
        result = _aggregate_by_product(items)
        assert len(result) == 1
        assert result[0].total_qty == 5.0
        assert result[0].total_omzet == 500000.0

    def test_deduplicates_same_product(self):
        """Same product+variant from different orders grouped together."""
        items = [
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=1, revenue=100000),
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=1, revenue=90000),
            LineItem(sku="S1", product_variant_label="Prod A - Red", quantity=1, revenue=110000),
        ]
        result = _aggregate_by_product(items)
        assert len(result) == 1
        assert result[0].total_qty == 3.0
        assert result[0].total_omzet == 300000.0


# ---------------------------------------------------------------------------
# _rank_top_products tests
# ---------------------------------------------------------------------------


class TestRankTopProducts:
    def test_sorts_by_omzet_descending(self):
        products = [
            AggregatedProduct("A - X", 10, 100000),
            AggregatedProduct("B - Y", 20, 300000),
            AggregatedProduct("C - Z", 15, 200000),
        ]
        ranked = _rank_top_products(products)
        assert ranked[0].product_variant_label == "B - Y"
        assert ranked[1].product_variant_label == "C - Z"
        assert ranked[2].product_variant_label == "A - X"

    def test_limit_max_round_20pct_20(self):
        """Limit = MAX(ROUND(unique × 20%), 20)."""
        # 100 products → ROUND(100 * 0.2) = 20, MAX(20, 20) = 20
        products = [
            AggregatedProduct(f"P{i} - V", 10, 1000 * (100 - i))
            for i in range(100)
        ]
        ranked = _rank_top_products(products)
        assert len(ranked) == 20

    def test_returns_all_if_fewer_than_20(self):
        """If fewer than 20 unique products, return all."""
        products = [
            AggregatedProduct(f"P{i} - V", 10, 1000 * (10 - i))
            for i in range(10)
        ]
        ranked = _rank_top_products(products)
        assert len(ranked) == 10

    def test_minimum_20_enforced(self):
        """With 50 products: ROUND(50 * 0.2) = 10, MAX(10, 20) = 20."""
        products = [
            AggregatedProduct(f"P{i} - V", 10, 1000 * (50 - i))
            for i in range(50)
        ]
        ranked = _rank_top_products(products)
        assert len(ranked) == 20

    def test_empty_input(self):
        ranked = _rank_top_products([])
        assert ranked == []

    def test_large_set_20pct_above_20(self):
        """With 200 products: ROUND(200 * 0.2) = 40, MAX(40, 20) = 40."""
        products = [
            AggregatedProduct(f"P{i} - V", 10, 1000 * (200 - i))
            for i in range(200)
        ]
        ranked = _rank_top_products(products)
        assert len(ranked) == 40


# ---------------------------------------------------------------------------
# _build_mass_update_lookup tests
# ---------------------------------------------------------------------------


class TestBuildMassUpdateLookup:
    def test_builds_name_to_kode_mapping(self):
        mu_data = [
            {"Nama Produk": "Prod A", "Nama Variasi": "Red", "Kode Variasi": "K001", "Stok": 100},
            {"Nama Produk": "Prod B", "Nama Variasi": "Blue", "Kode Variasi": "K002", "Stok": 50},
        ]
        name_to_kode, _ = _build_mass_update_lookup(mu_data)
        assert name_to_kode["Prod A - Red"] == "K001"
        assert name_to_kode["Prod B - Blue"] == "K002"

    def test_builds_kode_to_stok_mapping(self):
        mu_data = [
            {"Nama Produk": "Prod A", "Nama Variasi": "Red", "Kode Variasi": "K001", "Stok": 100},
            {"Nama Produk": "Prod B", "Nama Variasi": "Blue", "Kode Variasi": "K002", "Stok": 50},
        ]
        _, kode_to_stok = _build_mass_update_lookup(mu_data)
        assert kode_to_stok["K001"] == 100
        assert kode_to_stok["K002"] == 50


# ---------------------------------------------------------------------------
# _enrich_with_mass_update tests
# ---------------------------------------------------------------------------


class TestEnrichWithMassUpdate:
    def _make_lookup(self):
        mu_data = [
            {"Nama Produk": "Prod A", "Nama Variasi": "Red", "Kode Variasi": "K001", "Stok": 100},
        ]
        return _build_mass_update_lookup(mu_data)

    def test_matches_by_label(self):
        top = [AggregatedProduct("Prod A - Red", 5, 500000)]
        line_items = [LineItem("S1", "Prod A - Red", 5, 500000)]
        enriched = _enrich_with_mass_update(top, line_items, self._make_lookup())
        assert enriched[0].kode_variasi == "K001"
        assert enriched[0].stok == 100

    def test_tidak_ditemukan_when_no_match(self):
        top = [AggregatedProduct("Prod C - Green", 3, 300000)]
        line_items = [LineItem("S3", "Prod C - Green", 3, 300000)]
        enriched = _enrich_with_mass_update(top, line_items, self._make_lookup())
        assert enriched[0].kode_variasi == "Kode Variasi tidak ditemukan"

    def test_stok_zero_when_kode_not_found(self):
        top = [AggregatedProduct("Prod C - Green", 3, 300000)]
        line_items = [LineItem("S3", "Prod C - Green", 3, 300000)]
        enriched = _enrich_with_mass_update(top, line_items, self._make_lookup())
        assert enriched[0].stok == 0

    def test_rata2_harga_jual_is_max_single_line_revenue(self):
        """rata2_harga_jual = max revenue across individual lines for that product."""
        top = [AggregatedProduct("Prod A - Red", 5, 500000)]
        line_items = [
            LineItem("S1", "Prod A - Red", 2, 200000),
            LineItem("S1", "Prod A - Red", 3, 387000),  # max
            LineItem("S1", "Prod A - Red", 1, 100000),
        ]
        enriched = _enrich_with_mass_update(top, line_items, self._make_lookup())
        assert enriched[0].rata2_harga_jual == 387000.0


# ---------------------------------------------------------------------------
# _calculate_average_stock tests
# ---------------------------------------------------------------------------


class TestCalculateAverageStock:
    def test_rounded_integer(self):
        products = [
            EnrichedProduct("A - X", 10, 100000, "K1", 100000, 100),
            EnrichedProduct("B - Y", 20, 200000, "K2", 200000, 150),
            EnrichedProduct("C - Z", 15, 150000, "K3", 150000, 120),
        ]
        # avg = (100 + 150 + 120) / 3 = 123.333 → 123
        assert _calculate_average_stock(products) == 123

    def test_empty_list(self):
        assert _calculate_average_stock([]) == 0

    def test_rounds_half_up(self):
        """Python's round() uses banker's rounding, testing a clear case."""
        products = [
            EnrichedProduct("A - X", 10, 100000, "K1", 100000, 125),
            EnrichedProduct("B - Y", 10, 100000, "K2", 100000, 126),
        ]
        # avg = (125 + 126) / 2 = 125.5 → 126 (banker's rounds to even)
        assert _calculate_average_stock(products) == 126


# ---------------------------------------------------------------------------
# _build_output_tables tests
# ---------------------------------------------------------------------------


class TestBuildOutputTables:
    def test_output_1_table_structure(self):
        products = [
            EnrichedProduct("KYPSO Sovereign - Cokelat Muda", 10, 4355000, "301913525888", 387000, 782),
        ]
        output_1, _ = _build_output_tables(products)
        assert len(output_1) == 1
        row = output_1[0]
        assert row["kode_variasi"] == "301913525888"
        assert row["product_name"] == "KYPSO Sovereign - Cokelat Muda"
        assert row["total_omzet"] == 4355000
        assert row["rata2_harga_jual"] == 387000

    def test_output_2_splits_nama_and_varian(self):
        products = [
            EnrichedProduct("KYPSO Sovereign - Cokelat Muda", 10, 4355000, "301913525888", 387000, 782),
        ]
        _, output_2 = _build_output_tables(products)
        assert len(output_2) == 1
        row = output_2[0]
        assert row["kode_variasi"] == "301913525888"
        assert row["nama_produk"] == "KYPSO Sovereign"
        assert row["varian"] == "Cokelat Muda"
        assert row["stok"] == 782

    def test_output_2_tidak_ditemukan(self):
        products = [
            EnrichedProduct("KYPSO Frontier - ", 5, 1887000, "Kode Variasi tidak ditemukan", 629000, 0),
        ]
        _, output_2 = _build_output_tables(products)
        row = output_2[0]
        assert row["kode_variasi"] == "Kode Variasi tidak ditemukan"
        assert row["stok"] == 0


# ---------------------------------------------------------------------------
# calculate_top_sku integration tests (unit-level)
# ---------------------------------------------------------------------------


class TestCalculateTopSku:
    def test_empty_order_data(self):
        result = calculate_top_sku([], [])
        assert result.output_text == ""
        assert result.details["output_1"] == []
        assert result.details["output_2"] == []
        assert result.details["average_stock"] == 0
        assert result.details["product_count"] == 0
        assert result.details["total_unique_products"] == 0

    def test_empty_mass_update_data(self):
        """Order data present but no mass update → all 'tidak ditemukan'."""
        order_data = [{
            "Nomor Referensi SKU": "SKU1",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 1,
            "Jumlah Produk di Pesan": 1,
            "Voucher Ditanggung Penjual": "0",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        result = calculate_top_sku(order_data, [])
        assert result.details["product_count"] == 1
        assert result.details["output_1"][0]["kode_variasi"] == "Kode Variasi tidak ditemukan"
        assert result.details["output_2"][0]["stok"] == 0
        assert result.details["average_stock"] == 0

    def test_single_product_single_order(self):
        order_data = [{
            "Nomor Referensi SKU": "SKU1",
            "Nama Produk": "Product A",
            "Nama Variasi": "Red",
            "Harga Setelah Diskon": "100.000",
            "Jumlah": 2,
            "Jumlah Produk di Pesan": 2,
            "Voucher Ditanggung Penjual": "10.000",
            "Cashback Koin": "0",
            "Diskon Dari Shopee": "0",
        }]
        mu_data = [
            {"Nama Produk": "Product A", "Nama Variasi": "Red", "Kode Variasi": "K001", "Stok": 50},
        ]
        result = calculate_top_sku(order_data, mu_data)
        assert result.details["product_count"] == 1
        assert result.details["total_unique_products"] == 1
        assert result.details["output_1"][0]["kode_variasi"] == "K001"
        assert result.details["output_2"][0]["stok"] == 50
        assert result.details["average_stock"] == 50

    def test_kypso_sample_pattern(self):
        """Verify KYPSO-like sample: 20 products, top product and avg stock pattern."""
        # Create 95 unique products (to get 20% = 19, but MIN 20)
        order_data = []
        mu_data = []
        for i in range(95):
            omzet_base = 5000000 - (i * 50000)  # Decreasing revenue
            order_data.append({
                "Nomor Referensi SKU": f"SKU{i:03d}",
                "Nama Produk": f"Product {i}",
                "Nama Variasi": f"Variant {i}",
                "Harga Setelah Diskon": str(omzet_base),
                "Jumlah": 1,
                "Jumlah Produk di Pesan": 1,
                "Voucher Ditanggung Penjual": "0",
                "Cashback Koin": "0",
                "Diskon Dari Shopee": "0",
            })
            mu_data.append({
                "Nama Produk": f"Product {i}",
                "Nama Variasi": f"Variant {i}",
                "Kode Variasi": f"K{i:03d}",
                "Stok": 100 + i,
            })

        result = calculate_top_sku(order_data, mu_data)
        # 95 products: ROUND(95 * 0.2) = 19, MAX(19, 20) = 20
        assert result.details["product_count"] == 20
        assert result.details["total_unique_products"] == 95
        # Top product has highest omzet
        assert result.details["output_1"][0]["product_name"] == "Product 0 - Variant 0"
        assert result.details["output_1"][0]["total_omzet"] == 5000000

    def test_mnd_sample_pattern(self):
        """Verify MND-like sample: 20 products, top product pattern."""
        # Create 100 unique products
        order_data = []
        mu_data = []
        for i in range(100):
            omzet_base = 20000000 - (i * 180000)
            order_data.append({
                "Nomor Referensi SKU": f"SKU{i:03d}",
                "Nama Produk": f"Product {i}",
                "Nama Variasi": f"Variant {i}",
                "Harga Setelah Diskon": str(omzet_base),
                "Jumlah": 1,
                "Jumlah Produk di Pesan": 1,
                "Voucher Ditanggung Penjual": "0",
                "Cashback Koin": "0",
                "Diskon Dari Shopee": "0",
            })
            mu_data.append({
                "Nama Produk": f"Product {i}",
                "Nama Variasi": f"Variant {i}",
                "Kode Variasi": f"MK{i:03d}",
                "Stok": 50 + (i * 2),
            })

        result = calculate_top_sku(order_data, mu_data)
        # 100 products: ROUND(100 * 0.2) = 20, MAX(20, 20) = 20
        assert result.details["product_count"] == 20
        assert result.details["total_unique_products"] == 100
        assert result.details["output_1"][0]["product_name"] == "Product 0 - Variant 0"
        assert result.details["output_1"][0]["total_omzet"] == 20000000
