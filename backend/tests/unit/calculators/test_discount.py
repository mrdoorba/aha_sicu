"""Unit tests for the Discount Check Calculator.

Tests against the spec in logic/calculator-3-discount-checkup.md
with SUKA, KYPSO, and MND sample data.
"""


import pytest

from app.calculators.discount import (
    DiscountResult,
    LineItem,
    ProductSummary,
    _build_product_summary,
    _calculate_line_items,
    _calculate_urutan,
    _filter_top_sku,
    _format_output,
    _roundup,
    _safe_num,
    calculate_discount,
)
from app.calculators.price_parser import _parse_price


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

    def test_float_string(self):
        assert _safe_num("3.14") == 3.14

    def test_non_numeric_string(self):
        assert _safe_num("abc") == 0.0

    def test_whitespace_string(self):
        assert _safe_num("  ") == 0.0

    def test_whitespace_dash(self):
        assert _safe_num(" - ") == 0.0


# ---------------------------------------------------------------------------
# _parse_price tests (via shared price_parser module)
# ---------------------------------------------------------------------------


class TestParsePrice:
    def test_removes_dots(self):
        assert _parse_price("125.000") == 125000.0

    def test_multiple_dots(self):
        assert _parse_price("1.250.000") == 1250000.0

    def test_zero_string(self):
        assert _parse_price("0") == 0.0

    def test_empty_string(self):
        assert _parse_price("") == 0.0

    def test_none(self):
        assert _parse_price(None) == 0.0

    def test_no_dots(self):
        assert _parse_price("5000") == 5000.0

    def test_integer_input(self):
        assert _parse_price(125000) == 125000.0

    def test_float_input(self):
        assert _parse_price(125000.5) == 125000.5

    def test_non_numeric(self):
        assert _parse_price("abc") == 0.0


# ---------------------------------------------------------------------------
# _calculate_urutan tests
# ---------------------------------------------------------------------------


class TestCalculateUrutan:
    def test_same_order_increments(self):
        rows = [
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": "ORD001"},
        ]
        assert _calculate_urutan(rows) == [1, 2, 3]

    def test_different_order_resets(self):
        rows = [
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": "ORD002"},
            {"No. Pesanan": "ORD002"},
        ]
        assert _calculate_urutan(rows) == [1, 2, 1, 2]

    def test_empty_order_skips(self):
        rows = [
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": ""},
            {"No. Pesanan": "ORD002"},
        ]
        assert _calculate_urutan(rows) == [1, 0, 1]

    def test_none_order_skips(self):
        rows = [
            {"No. Pesanan": None},
            {"No. Pesanan": "ORD001"},
        ]
        assert _calculate_urutan(rows) == [0, 1]

    def test_single_order(self):
        rows = [{"No. Pesanan": "ORD001"}]
        assert _calculate_urutan(rows) == [1]

    def test_empty_rows(self):
        assert _calculate_urutan([]) == []


# ---------------------------------------------------------------------------
# Line item calculation tests
# ---------------------------------------------------------------------------


class TestCalculateLineItems:
    def test_total_discount_formula(self):
        """N = (Harga Awal - Harga Setelah Diskon) + Voucher + Paket."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "2",
                "Voucher Ditanggung Penjual": "5.000",
                "Paket Diskon (Diskon dari Penjual)": "3.000",
            },
        ]
        urutan = [1]
        items = _calculate_line_items(rows, urutan)
        assert len(items) == 1
        # N = (100000 - 80000) + 5000 + 3000 = 28000
        assert items[0].total_discount == 28000.0

    def test_discount_percentage(self):
        """O = N / Harga Awal."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ]
        urutan = [1]
        items = _calculate_line_items(rows, urutan)
        # N = 20000, O = 20000 / 100000 = 0.2
        assert items[0].discount_pct == pytest.approx(0.2)

    def test_total_paid(self):
        """P = Harga Setelah Diskon - Voucher - Paket."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "5.000",
                "Paket Diskon (Diskon dari Penjual)": "3.000",
            },
        ]
        urutan = [1]
        items = _calculate_line_items(rows, urutan)
        # P = 80000 - 5000 - 3000 = 72000
        assert items[0].total_paid == 72000.0

    def test_voucher_applied_only_urutan_1(self):
        """Voucher = 0 when Urutan > 1."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "5.000",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product B",
                "Harga Awal": "50.000",
                "Harga Setelah Diskon": "40.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "5.000",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ]
        urutan = [1, 2]
        items = _calculate_line_items(rows, urutan)
        assert items[0].voucher == 5000.0  # Urutan=1
        assert items[1].voucher == 0.0     # Urutan=2

    def test_paket_applied_only_urutan_1(self):
        """Paket = 0 when Urutan > 1."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "3.000",
            },
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product B",
                "Harga Awal": "50.000",
                "Harga Setelah Diskon": "40.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "3.000",
            },
        ]
        urutan = [1, 2]
        items = _calculate_line_items(rows, urutan)
        assert items[0].paket == 3000.0  # Urutan=1
        assert items[1].paket == 0.0     # Urutan=2

    def test_skips_urutan_zero(self):
        """Rows with Urutan=0 (empty order) are skipped."""
        rows = [
            {
                "No. Pesanan": "",
                "Nama Produk": "Product A",
                "Harga Awal": "100.000",
                "Harga Setelah Diskon": "80.000",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ]
        urutan = [0]
        items = _calculate_line_items(rows, urutan)
        assert len(items) == 0

    def test_zero_harga_awal(self):
        """Zero Harga Awal → discount_pct = 0 (no division by zero)."""
        rows = [
            {
                "No. Pesanan": "ORD001",
                "Nama Produk": "Product A",
                "Harga Awal": "0",
                "Harga Setelah Diskon": "0",
                "Jumlah": "1",
                "Voucher Ditanggung Penjual": "0",
                "Paket Diskon (Diskon dari Penjual)": "0",
            },
        ]
        urutan = [1]
        items = _calculate_line_items(rows, urutan)
        assert items[0].discount_pct == 0.0


# ---------------------------------------------------------------------------
# Product summary tests
# ---------------------------------------------------------------------------


class TestBuildProductSummary:
    def test_groups_by_name_only(self):
        """Groups by Nama Produk exact match (NOT including variant)."""
        items = [
            LineItem(
                harga_awal=100000, harga_setelah_diskon=80000,
                voucher=0, paket=0, jumlah=2, nama_produk="Product A",
                total_discount=20000, discount_pct=0.2, total_paid=80000, urutan=1,
            ),
            LineItem(
                harga_awal=100000, harga_setelah_diskon=90000,
                voucher=0, paket=0, jumlah=3, nama_produk="Product A",
                total_discount=10000, discount_pct=0.1, total_paid=90000, urutan=1,
            ),
            LineItem(
                harga_awal=50000, harga_setelah_diskon=40000,
                voucher=0, paket=0, jumlah=1, nama_produk="Product B",
                total_discount=10000, discount_pct=0.2, total_paid=40000, urutan=1,
            ),
        ]
        summary = _build_product_summary(items)
        assert len(summary) == 2

        a = next(p for p in summary if p.product_name == "Product A")
        assert a.qty == 5  # 2 + 3
        assert a.avg_discount_pct == pytest.approx(0.15)  # avg(0.2, 0.1)

        b = next(p for p in summary if p.product_name == "Product B")
        assert b.qty == 1
        assert b.avg_discount_pct == pytest.approx(0.2)

    def test_empty_product_name_skipped(self):
        """Lines with empty product name are skipped."""
        items = [
            LineItem(
                harga_awal=100000, harga_setelah_diskon=80000,
                voucher=0, paket=0, jumlah=1, nama_produk="",
                total_discount=20000, discount_pct=0.2, total_paid=80000, urutan=1,
            ),
        ]
        summary = _build_product_summary(items)
        assert len(summary) == 0


# ---------------------------------------------------------------------------
# TOP SKU filter tests
# ---------------------------------------------------------------------------


class TestFilterTopSku:
    def test_filters_qty_above_average(self):
        """Only products with qty > average qualify."""
        products = [
            ProductSummary("A", qty=10, avg_discount_pct=0.05),
            ProductSummary("B", qty=5, avg_discount_pct=0.05),
            ProductSummary("C", qty=2, avg_discount_pct=0.05),
        ]
        # avg = (10+5+2)/3 = 5.67, limit = round(3*0.2) = round(0.6) = 1
        top = _filter_top_sku(products)
        assert len(top) == 1
        assert top[0].product_name == "A"  # qty=10 > 5.67

    def test_excludes_100pct_discount(self):
        """Products with avg_disc >= 1.0 (100%) excluded."""
        products = [
            ProductSummary("A", qty=10, avg_discount_pct=1.0),   # excluded
            ProductSummary("B", qty=8, avg_discount_pct=0.5),    # included
            ProductSummary("C", qty=2, avg_discount_pct=0.05),   # qty below avg
        ]
        # avg = (10+8+2)/3 = 6.67, limit = round(3*0.2) = 1
        top = _filter_top_sku(products)
        assert len(top) == 1
        assert top[0].product_name == "B"

    def test_limit_formula(self):
        """Limit = ROUND(unique_products * 20%), no minimum floor."""
        products = [
            ProductSummary(f"P{i}", qty=100 - i, avg_discount_pct=0.05)
            for i in range(10)
        ]
        # avg qty = (100+99+...+91)/10 = 95.5
        # All above 95.5: P0(100), P1(99), P2(98), P3(97), P4(96)
        # Limit = round(10 * 0.2) = 2
        top = _filter_top_sku(products)
        assert len(top) == 2
        assert top[0].product_name == "P0"
        assert top[1].product_name == "P1"

    def test_limit_no_minimum_floor(self):
        """No MIN(20) floor unlike Calculator 2."""
        # 3 products → limit = round(3 * 0.2) = round(0.6) = 1
        products = [
            ProductSummary("A", qty=10, avg_discount_pct=0.05),
            ProductSummary("B", qty=5, avg_discount_pct=0.05),
            ProductSummary("C", qty=2, avg_discount_pct=0.05),
        ]
        top = _filter_top_sku(products)
        assert len(top) <= 1

    def test_empty_input(self):
        assert _filter_top_sku([]) == []

    def test_ordered_by_qty_descending(self):
        """TOP SKU ordered by qty descending."""
        products = [
            ProductSummary("A", qty=5, avg_discount_pct=0.05),
            ProductSummary("B", qty=20, avg_discount_pct=0.05),
            ProductSummary("C", qty=15, avg_discount_pct=0.05),
            ProductSummary("D", qty=1, avg_discount_pct=0.05),
            ProductSummary("E", qty=1, avg_discount_pct=0.05),
        ]
        # avg = (5+20+15+1+1)/5 = 8.4
        # Above avg: B(20), C(15)
        # Limit = round(5*0.2) = 1
        top = _filter_top_sku(products)
        assert len(top) == 1
        assert top[0].product_name == "B"


# ---------------------------------------------------------------------------
# ROUNDUP tests
# ---------------------------------------------------------------------------


class TestRoundup:
    def test_roundup_3_decimals(self):
        """ROUNDUP(0.06698, 3) = 0.067."""
        assert _roundup(0.06698, 3) == pytest.approx(0.067)

    def test_roundup_already_exact(self):
        """ROUNDUP(0.067, 3) = 0.067."""
        assert _roundup(0.067, 3) == pytest.approx(0.067)

    def test_roundup_zero(self):
        assert _roundup(0.0, 3) == 0.0

    def test_roundup_small_fraction(self):
        """ROUNDUP(0.001, 3) = 0.001."""
        assert _roundup(0.001, 3) == pytest.approx(0.001)


# ---------------------------------------------------------------------------
# Output format tests
# ---------------------------------------------------------------------------


class TestFormatOutput:
    def _make_items(self, n_values, p_values, voucher_values=None,
                    paket_values=None, hsd_values=None):
        """Create line items with specified N, P, voucher, paket values."""
        items = []
        for i, (n, p) in enumerate(zip(n_values, p_values)):
            v = voucher_values[i] if voucher_values else 0
            pk = paket_values[i] if paket_values else 0
            hsd = hsd_values[i] if hsd_values else (p + v + pk)
            items.append(LineItem(
                harga_awal=n + hsd, harga_setelah_diskon=hsd,
                voucher=v, paket=pk, jumlah=1,
                nama_produk=f"Product {i}", total_discount=n,
                discount_pct=n / (n + hsd) if (n + hsd) > 0 else 0,
                total_paid=p, urutan=1,
            ))
        return items

    def test_discount_pct_uses_all_lines(self):
        """Output 1: SUMIF(P>0, N) / SUM(P) uses ALL lines."""
        items = self._make_items(
            n_values=[1000, 2000, 500],
            p_values=[10000, 20000, 5000],
        )
        top_sku = [ProductSummary("P", qty=1, avg_discount_pct=0.05)]
        output_text, details = _format_output(items, top_sku)
        # SUMIF(P>0, N) = 1000+2000+500 = 3500
        # SUM(P) = 35000
        # 3500/35000 = 0.1 = 10.0%
        assert "% Diskon TOP SKU: 10.0%" in output_text

    def test_discount_pct_excludes_negative_p_from_n(self):
        """Output 1: N is only summed where P > 0."""
        items = self._make_items(
            n_values=[1000, 2000],
            p_values=[10000, -5000],
        )
        top_sku = []
        output_text, details = _format_output(items, top_sku)
        # SUMIF(P>0, N) = 1000 (only first, second has P=-5000)
        # SUM(P) = 10000 + (-5000) = 5000
        # 1000/5000 = 0.2 = 20.0%
        assert "% Diskon TOP SKU: 20.0%" in output_text

    def test_range_roundup_3_decimals(self):
        """Output 2: Range uses ROUNDUP to 3 decimal places."""
        top_sku = [
            ProductSummary("A", qty=10, avg_discount_pct=0.06698),
            ProductSummary("B", qty=8, avg_discount_pct=0.00001),
        ]
        items = self._make_items([0], [1])
        output_text, _ = _format_output(items, top_sku)
        # ROUNDUP(0.00001, 3) = 0.001 → 0.1%
        # ROUNDUP(0.06698, 3) = 0.067 → 6.7%
        assert "Range: 0.1% ~ 6.7%" in output_text

    def test_voucher_pct_denominator_is_after_discount(self):
        """Output 3: Voucher denominator is Harga Setelah Diskon, NOT Harga Awal."""
        items = [
            LineItem(
                harga_awal=100000, harga_setelah_diskon=80000,
                voucher=2400, paket=0, jumlah=1, nama_produk="A",
                total_discount=22400, discount_pct=0.224, total_paid=77600, urutan=1,
            ),
        ]
        _, details = _format_output(items, [])
        # voucher_pct = 2400 / 80000 = 0.03 = 3.0%
        assert details["voucher_pct"] == "3.0%"

    def test_paket_pct(self):
        """Output 4: Paket Diskon %."""
        items = [
            LineItem(
                harga_awal=100000, harga_setelah_diskon=80000,
                voucher=0, paket=1600, jumlah=1, nama_produk="A",
                total_discount=21600, discount_pct=0.216, total_paid=78400, urutan=1,
            ),
        ]
        _, details = _format_output(items, [])
        # paket_pct = 1600 / 80000 = 0.02 = 2.0%
        assert details["paket_pct"] == "2.0%"

    def test_fake_discount_above_20pct(self):
        """Output 5: Flag triggered when SUM(N)/SUM(P) > 20%."""
        items = self._make_items(
            n_values=[3000],
            p_values=[10000],
        )
        output_text, details = _format_output(items, [])
        # 3000/10000 = 30% > 20%
        assert "📌" in output_text
        assert details["fake_discount_flag"] is True

    def test_fake_discount_below_20pct(self):
        """Output 5: No flag when SUM(N)/SUM(P) <= 20%."""
        items = self._make_items(
            n_values=[1000],
            p_values=[10000],
        )
        output_text, details = _format_output(items, [])
        # 1000/10000 = 10% < 20%
        assert "📌" not in output_text
        assert details["fake_discount_flag"] is False

    def test_fake_discount_exactly_20pct(self):
        """Output 5: No flag at exactly 20% (> 20%, not >=)."""
        items = self._make_items(
            n_values=[2000],
            p_values=[10000],
        )
        output_text, details = _format_output(items, [])
        # 2000/10000 = 20% NOT > 20%
        assert "📌" not in output_text
        assert details["fake_discount_flag"] is False


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------


def _make_order_row(
    order_num: str,
    product: str,
    harga_awal: str,
    harga_diskon: str,
    jumlah: str = "1",
    voucher: str = "0",
    paket: str = "0",
) -> dict:
    """Helper to build an order export row."""
    return {
        "No. Pesanan": order_num,
        "Nama Produk": product,
        "Harga Awal": harga_awal,
        "Harga Setelah Diskon": harga_diskon,
        "Jumlah": jumlah,
        "Voucher Ditanggung Penjual": voucher,
        "Paket Diskon (Diskon dari Penjual)": paket,
    }


# SUKA-pattern sample — synthetic data that exercises the no-flag path.
# Produces low discount ratios without fake discount trigger.

SUKA_DATA = [
    # Order 1: 2 items
    _make_order_row("SUKA001", "Sepatu Sneakers", "200.000", "195.000", "1", "3.000", "0"),
    _make_order_row("SUKA001", "Kaos Polos", "50.000", "48.000", "2", "3.000", "0"),
    # Order 2: 1 item
    _make_order_row("SUKA002", "Sepatu Sneakers", "200.000", "190.000", "1", "2.000", "0"),
    # Order 3: 1 item
    _make_order_row("SUKA003", "Tas Ransel", "150.000", "150.000", "1", "0", "0"),
    # Order 4: 2 items
    _make_order_row("SUKA004", "Sepatu Sneakers", "200.000", "195.000", "2", "1.000", "0"),
    _make_order_row("SUKA004", "Topi Baseball", "75.000", "72.000", "1", "1.000", "0"),
    # Order 5: 1 item
    _make_order_row("SUKA005", "Kaos Polos", "50.000", "49.000", "3", "0", "0"),
    # Order 6: 1 item
    _make_order_row("SUKA006", "Tas Ransel", "150.000", "148.000", "1", "0", "0"),
    # Order 7: 1 item — high volume product
    _make_order_row("SUKA007", "Sepatu Sneakers", "200.000", "198.000", "3", "0", "0"),
    # Order 8: 1 item
    _make_order_row("SUKA008", "Kaos Polos", "50.000", "49.000", "4", "0", "0"),
    # Order 9: 1 item
    _make_order_row("SUKA009", "Sepatu Sneakers", "200.000", "194.000", "2", "0", "0"),
    # Order 10: 1 item
    _make_order_row("SUKA010", "Tas Ransel", "150.000", "150.000", "2", "500", "0"),
]


# KYPSO-pattern sample — synthetic data that exercises the fake discount flag path.
# Heavy discounts trigger the >20% threshold.
KYPSO_DATA = [
    # Order 1: heavily discounted (70% off + voucher)
    _make_order_row("KYP001", "Cream Wajah Premium", "500.000", "150.000", "1", "50.000", "0"),
    _make_order_row("KYP001", "Serum Anti Aging", "300.000", "90.000", "1", "50.000", "0"),
    # Order 2: heavily discounted
    _make_order_row("KYP002", "Cream Wajah Premium", "500.000", "145.000", "2", "40.000", "0"),
    # Order 3: heavily discounted
    _make_order_row("KYP003", "Masker Organik", "200.000", "60.000", "1", "10.000", "0"),
    # Order 4: heavily discounted
    _make_order_row("KYP004", "Cream Wajah Premium", "500.000", "140.000", "1", "30.000", "0"),
    _make_order_row("KYP004", "Toner Herbal", "250.000", "75.000", "1", "30.000", "0"),
    # Order 5: heavily discounted
    _make_order_row("KYP005", "Serum Anti Aging", "300.000", "85.000", "2", "20.000", "0"),
    # Order 6: heavily discounted
    _make_order_row("KYP006", "Masker Organik", "200.000", "55.000", "1", "5.000", "0"),
    # Order 7: heavily discounted
    _make_order_row("KYP007", "Cream Wajah Premium", "500.000", "150.000", "3", "0", "0"),
    # Order 8: heavily discounted
    _make_order_row("KYP008", "Serum Anti Aging", "300.000", "80.000", "1", "0", "0"),
]


# MND-pattern sample — synthetic data with voucher + paket + fake discount flag.
MND_DISCOUNT_DATA = [
    # Order 1: big discount + voucher + paket
    _make_order_row("MND001", "MOON DAE Nami Bag", "250.000", "125.000", "1", "20.000", "5.000"),
    _make_order_row("MND001", "MOON DAE Seoul Bag", "200.000", "100.000", "1", "20.000", "5.000"),
    # Order 2
    _make_order_row("MND002", "MOON DAE Nami Bag", "250.000", "120.000", "2", "15.000", "3.000"),
    # Order 3
    _make_order_row("MND003", "MOON DAE Bona Bag", "180.000", "90.000", "1", "10.000", "2.000"),
    # Order 4: multiple items
    _make_order_row("MND004", "MOON DAE Nami Bag", "250.000", "125.000", "1", "25.000", "5.000"),
    _make_order_row("MND004", "MOON DAE Honey Bag", "220.000", "110.000", "1", "25.000", "5.000"),
    # Order 5
    _make_order_row("MND005", "MOON DAE Seoul Bag", "200.000", "95.000", "2", "20.000", "4.000"),
    # Order 6
    _make_order_row("MND006", "MOON DAE Bona Bag", "180.000", "85.000", "1", "15.000", "3.000"),
    # Order 7
    _make_order_row("MND007", "MOON DAE Nami Bag", "250.000", "120.000", "3", "10.000", "2.000"),
    # Order 8
    _make_order_row("MND008", "MOON DAE Honey Bag", "220.000", "105.000", "1", "8.000", "1.000"),
]


# ---------------------------------------------------------------------------
# Sample output tests (AC #8)
# ---------------------------------------------------------------------------


class TestNoFlagPattern:
    """Synthetic low-discount data — exercises the no-flag output path."""

    def test_no_fake_discount_flag(self):
        """Low discount ratio → no fake discount flag."""
        result = calculate_discount(SUKA_DATA)
        assert "📌" not in result.output_text

    def test_output_format_4_lines(self):
        """Output has exactly 4 lines (no flag line)."""
        result = calculate_discount(SUKA_DATA)
        lines = result.output_text.split("\n")
        assert lines[0].startswith("% Diskon TOP SKU:")
        assert lines[1].startswith("Range:")
        assert lines[2].startswith("Voucher ")
        assert lines[3].startswith("Paket Diskon ")
        assert len(lines) == 4

    def test_details_structure(self):
        """Details contain all required fields with correct types."""
        result = calculate_discount(SUKA_DATA)
        assert "discount_pct" in result.details
        assert "range_min" in result.details
        assert "range_max" in result.details
        assert "voucher_pct" in result.details
        assert "paket_pct" in result.details
        assert "fake_discount_flag" in result.details
        assert "product_summary" in result.details
        assert "top_sku" in result.details
        assert "totals" in result.details
        assert result.details["fake_discount_flag"] is False


class TestFakeDiscountFlagPattern:
    """Synthetic heavy-discount data — exercises the fake discount flag path."""

    def test_kypso_pattern_flag_triggered(self):
        """Heavy discounts trigger fake discount flag."""
        result = calculate_discount(KYPSO_DATA)
        assert "📌" in result.output_text
        assert result.details["fake_discount_flag"] is True

    def test_kypso_pattern_has_5_lines(self):
        """Flag output has 5 lines."""
        result = calculate_discount(KYPSO_DATA)
        lines = result.output_text.split("\n")
        assert len(lines) == 5
        assert "Berpotensi menggunakan 'fake discount'" in lines[4]


class TestMndEndToEndExactValues:
    """End-to-end regression test with exact value assertions.

    Uses MND-pattern synthetic data to verify all formulas integrate
    correctly and produce deterministic output.
    """

    def test_mnd_exact_output_text(self):
        """MND synthetic data produces exact expected output text."""
        result = calculate_discount(MND_DISCOUNT_DATA)
        expected = (
            "% Diskon TOP SKU: 137.3%\n"
            "Range: 59.5% ~ 59.5%\n"
            "Voucher 11.4%\n"
            "Paket Diskon 2.3%\n"
            "📌 Berpotensi menggunakan 'fake discount'"
        )
        assert result.output_text == expected

    def test_mnd_exact_detail_values(self):
        """MND synthetic data produces exact detail values."""
        result = calculate_discount(MND_DISCOUNT_DATA)
        assert result.details["discount_pct"] == "137.3%"
        assert result.details["range_min"] == "59.5%"
        assert result.details["range_max"] == "59.5%"
        assert result.details["voucher_pct"] == "11.4%"
        assert result.details["paket_pct"] == "2.3%"
        assert result.details["fake_discount_flag"] is True

    def test_mnd_exact_totals(self):
        """MND synthetic data produces exact totals."""
        result = calculate_discount(MND_DISCOUNT_DATA)
        totals = result.details["totals"]
        assert totals["sum_n"] == pytest.approx(1273000.0)
        assert totals["sum_p"] == pytest.approx(927000.0)
        assert totals["sum_voucher"] == pytest.approx(123000.0)
        assert totals["sum_paket"] == pytest.approx(25000.0)
        assert totals["sum_harga_setelah_diskon"] == pytest.approx(1075000.0)

    def test_mnd_product_summary_count(self):
        """MND has 4 unique products."""
        result = calculate_discount(MND_DISCOUNT_DATA)
        assert len(result.details["product_summary"]) == 4

    def test_mnd_top_sku_selection(self):
        """MND top SKU is MOON DAE Nami Bag (highest qty above average)."""
        result = calculate_discount(MND_DISCOUNT_DATA)
        top = result.details["top_sku"]
        assert len(top) == 1
        assert top[0]["product_name"] == "MOON DAE Nami Bag"
        assert top[0]["qty"] == 7.0


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_data_handling(self):
        """Empty data returns zeros."""
        result = calculate_discount([])
        assert "0.0%" in result.output_text
        assert result.details["fake_discount_flag"] is False

    def test_single_order_single_item(self):
        """Single order with single item."""
        data = [
            _make_order_row("ORD001", "Product A", "100.000", "80.000", "1", "0", "0"),
        ]
        result = calculate_discount(data)
        assert isinstance(result, DiscountResult)
        assert "% Diskon TOP SKU:" in result.output_text

    def test_all_zero_prices(self):
        """All zero prices shouldn't crash."""
        data = [
            _make_order_row("ORD001", "Product A", "0", "0", "1", "0", "0"),
            _make_order_row("ORD002", "Product B", "0", "0", "1", "0", "0"),
        ]
        result = calculate_discount(data)
        assert isinstance(result, DiscountResult)

    def test_all_same_product(self):
        """All lines are the same product."""
        data = [
            _make_order_row("ORD001", "Product A", "100.000", "80.000", "1", "0", "0"),
            _make_order_row("ORD002", "Product A", "100.000", "80.000", "2", "0", "0"),
            _make_order_row("ORD003", "Product A", "100.000", "80.000", "3", "0", "0"),
        ]
        result = calculate_discount(data)
        assert len(result.details["product_summary"]) == 1

    def test_result_type(self):
        """Returns DiscountResult."""
        data = [
            _make_order_row("ORD001", "Product A", "100.000", "80.000", "1", "0", "0"),
        ]
        result = calculate_discount(data)
        assert isinstance(result, DiscountResult)
        assert isinstance(result.output_text, str)
        assert isinstance(result.details, dict)

    def test_details_has_all_keys(self):
        """Details dict contains all required keys."""
        data = [
            _make_order_row("ORD001", "Product A", "100.000", "80.000", "1", "0", "0"),
        ]
        result = calculate_discount(data)
        expected_keys = {
            "discount_pct", "range_min", "range_max",
            "voucher_pct", "paket_pct", "fake_discount_flag",
            "product_summary", "top_sku", "totals",
        }
        assert set(result.details.keys()) == expected_keys

    def test_totals_structure(self):
        """Totals dict has all required fields."""
        data = [
            _make_order_row("ORD001", "Product A", "100.000", "80.000", "1", "5.000", "3.000"),
        ]
        result = calculate_discount(data)
        totals = result.details["totals"]
        assert "sum_n" in totals
        assert "sum_p" in totals
        assert "sum_voucher" in totals
        assert "sum_paket" in totals
        assert "sum_harga_setelah_diskon" in totals
