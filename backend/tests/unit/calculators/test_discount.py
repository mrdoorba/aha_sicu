"""Unit tests for the sheet-parity discount calculator."""

from dataclasses import dataclass

import pytest

from app.calculators.discount import (
    DiscountResult,
    _build_product_summary,
    _build_reference_price_map,
    _calculate_line_items,
    _calculate_urutan,
    _compute_fake_discount_gate,
    _filter_top_sku,
    _normalize_rows,
    _roundup,
    _safe_num,
    calculate_discount,
)


def _make_row(
    order_num: str,
    product: str,
    variant: str,
    harga_awal: str,
    harga_diskon: str,
    *,
    jumlah: str = "1",
    seller_discount: str = "0",
    shopee_discount: str = "0",
    voucher: str = "0",
    cashback: str = "0",
    paket: str = "0",
) -> dict:
    return {
        "No. Pesanan": order_num,
        "Nama Produk": product,
        "Nama Variasi": variant,
        "Harga Awal": harga_awal,
        "Harga Setelah Diskon": harga_diskon,
        "Jumlah": jumlah,
        "Diskon Dari Penjual": seller_discount,
        "Diskon Dari Shopee": shopee_discount,
        "Voucher Ditanggung Penjual": voucher,
        "Cashback Koin": cashback,
        "Paket Diskon (Diskon dari Penjual)": paket,
    }


MND_DATA = [
    _make_row("MND001", "MOON DAE Nami Bag", "", "250000", "125000", seller_discount="125000", voucher="20000", paket="5000"),
    _make_row("MND001", "MOON DAE Seoul Bag", "", "200000", "100000", seller_discount="100000", voucher="20000", paket="5000"),
    _make_row("MND002", "MOON DAE Nami Bag", "", "250000", "120000", jumlah="2", seller_discount="115000", voucher="15000", paket="3000"),
    _make_row("MND003", "MOON DAE Bona Bag", "", "180000", "90000", seller_discount="90000", voucher="10000", paket="2000"),
    _make_row("MND004", "MOON DAE Nami Bag", "", "250000", "125000", seller_discount="125000", voucher="25000", paket="5000"),
    _make_row("MND004", "MOON DAE Honey Bag", "", "220000", "110000", seller_discount="110000", voucher="25000", paket="5000"),
    _make_row("MND005", "MOON DAE Seoul Bag", "", "200000", "95000", jumlah="2", seller_discount="105000", voucher="20000", paket="4000"),
    _make_row("MND006", "MOON DAE Bona Bag", "", "180000", "85000", seller_discount="95000", voucher="15000", paket="3000"),
    _make_row("MND007", "MOON DAE Nami Bag", "", "250000", "120000", jumlah="3", seller_discount="130000", voucher="10000", paket="2000"),
    _make_row("MND008", "MOON DAE Honey Bag", "", "220000", "105000", seller_discount="115000", voucher="8000", paket="1000"),
]


LOW_FLAG_DATA = [
    _make_row("LOW001", "Product A", "V1", "100", "95", seller_discount="5"),
    _make_row("LOW002", "Product B", "V1", "100", "95", seller_discount="5"),
]


class TestSafeNum:
    def test_handles_empty_and_numeric_values(self):
        assert _safe_num(None) == 0.0
        assert _safe_num(5) == 5.0
        assert _safe_num("3.14") == 3.14
        assert _safe_num(" - ") == 0.0
        assert _safe_num("abc") == 0.0


class TestLegacyHelpers:
    def test_calculate_urutan_is_still_stable(self):
        rows = [
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": "ORD001"},
            {"No. Pesanan": ""},
            {"No. Pesanan": "ORD002"},
        ]
        assert _calculate_urutan(rows) == [1, 2, 0, 1]

    def test_roundup_three_decimals(self):
        assert _roundup(0.0018607, 3) == pytest.approx(0.002)


class TestSheetStages:
    def test_zero_seller_discount_on_paid_row_yields_zero_pct_not_blank(self):
        items = _normalize_rows(
            [
                _make_row("O1", "Prod", "V1", "100", "100", seller_discount="0"),
            ]
        )
        assert items[0].seller_discount_pct == 0.0

    def test_free_item_keeps_seller_discount_pct_blank(self):
        items = _normalize_rows(
            [
                _make_row("O1", "Gift", "V1", "100", "0", seller_discount="0"),
            ]
        )
        assert items[0].seller_discount_pct is None

    def test_reference_price_outlier_cap_excludes_high_value(self):
        items = _normalize_rows(
            [
                _make_row("O1", "Prod", "V1", "500", "500"),
                _make_row("O2", "Prod", "V1", "500", "500"),
                _make_row("O3", "Prod", "V1", "500", "500"),
                _make_row("O4", "Prod", "V1", "1000", "1000"),
            ]
        )
        ref_map = _build_reference_price_map(items, fake_discount_gate=False)
        assert ref_map["ProdV1"] == 500.0

    def test_reference_price_uses_harga_setelah_diskon_when_fake_gate_true(self):
        items = _normalize_rows(
            [
                _make_row("O1", "Prod", "V1", "100", "50", seller_discount="40"),
                _make_row("O2", "Prod", "V1", "100", "70", seller_discount="30"),
            ]
        )
        assert _compute_fake_discount_gate(items) is True
        ref_map = _build_reference_price_map(items, fake_discount_gate=True)
        assert ref_map["ProdV1"] == 70.0

    def test_voucher_is_split_by_order_row_count(self):
        rows = [
            _make_row("O1", "Prod A", "V1", "100", "80", voucher="6"),
            _make_row("O1", "Prod B", "V1", "100", "80", voucher="6"),
        ]
        items = _calculate_line_items(rows, _calculate_urutan(rows))
        assert [item.campaign_discount for item in items] == [23.0, 23.0]

    def test_paket_is_split_by_order_row_count(self):
        rows = [
            _make_row("O1", "Prod A", "V1", "100", "80", paket="4"),
            _make_row("O1", "Prod B", "V1", "100", "80", paket="4"),
        ]
        items = _calculate_line_items(rows, _calculate_urutan(rows))
        assert [item.campaign_discount for item in items] == [22.0, 22.0]

    def test_composite_key_grouping_keeps_variants_separate(self):
        rows = [
            _make_row("O1", "Prod", "Red", "100", "80"),
            _make_row("O2", "Prod", "Blue", "100", "80"),
        ]
        items = _calculate_line_items(rows, _calculate_urutan(rows))
        summary = _build_product_summary(items)
        assert [item.product_name for item in summary] == ["ProdRed", "ProdBlue"]

    def test_filter_top_sku_limit_is_20_percent_of_unique_products(self):
        @dataclass
        class SummaryStub:
            product_name: str
            qty: float
            avg_discount_pct: float

        summary = [SummaryStub(product_name=f"P{i}", qty=100 - i, avg_discount_pct=0.1) for i in range(10)]
        top = _filter_top_sku(summary)
        assert len(top) == 2

    def test_filter_top_sku_excludes_zero_and_negative_discounts(self):
        @dataclass
        class SummaryStub:
            product_name: str
            qty: float
            avg_discount_pct: float

        summary = [
            SummaryStub("zero", qty=100, avg_discount_pct=0.0),
            SummaryStub("negative", qty=90, avg_discount_pct=-0.05),
            SummaryStub("positive", qty=80, avg_discount_pct=0.10),
            SummaryStub("small", qty=1, avg_discount_pct=0.02),
            SummaryStub("also_small", qty=1, avg_discount_pct=0.03),
        ]

        top = _filter_top_sku(summary)

        assert [item.product_name for item in top] == ["positive"]


class TestPublicContract:
    def test_empty_data_returns_zero_safe_contract(self):
        result = calculate_discount([])
        assert result.output_text == (
            "% Diskon TOP SKU: 0.0%\n"
            "Range: 0.0% ~ 0.0%\n"
            "Voucher 0.0%\n"
            "Paket Diskon 0.0%\n"
            "% Komisi Afiliasi: 0.0%"
        )
        assert result.details["fake_discount_flag"] is False
        assert result.details["top_sku"] == []
        assert result.details["product_summary"] == []

    def test_contract_shape_stays_stable(self):
        result = calculate_discount([_make_row("O1", "A", "V1", "100", "80", seller_discount="25")])
        expected_keys = {
            "discount_pct",
            "range_min",
            "range_max",
            "voucher_pct",
            "paket_pct",
            "discount_pct_raw",
            "range_min_raw",
            "range_max_raw",
            "voucher_pct_raw",
            "paket_pct_raw",
            "affiliate_commission_pct",
            "affiliate_commission_pct_raw",
            "fake_discount_flag",
            "i18n",
            "product_summary",
            "top_sku",
            "totals",
        }
        assert isinstance(result, DiscountResult)
        assert set(result.details.keys()) == expected_keys

    def test_affiliate_commission_pct_uses_current_month_revenue(self):
        result = calculate_discount(
            LOW_FLAG_DATA,
            affiliate_commission=500_000,
            current_month_revenue=10_000_000,
        )

        assert result.details["affiliate_commission_pct"] == "5.0%"
        assert result.details["affiliate_commission_pct_raw"] == pytest.approx(0.05)
        assert "% Komisi Afiliasi: 5.0%" in result.output_text

    def test_i18n_fake_discount_key_only_present_when_flagged(self):
        flagged = calculate_discount(MND_DATA)
        unflagged = calculate_discount(LOW_FLAG_DATA)
        assert flagged.details["i18n"]["fakeDiscount"]["key"] == "discount.output.fakeDiscount"
        assert "fakeDiscount" not in unflagged.details["i18n"]
        assert unflagged.details["i18n"]["affiliateCommission"]["key"] == "discount.output.affiliateCommission"


class TestEndToEndParityFixtures:
    def test_fake_gate_uses_average_seller_discount_with_zero_discount_rows_included(self):
        result = calculate_discount(LOW_FLAG_DATA)
        assert result.details["fake_discount_flag"] is False

        high_flag = calculate_discount([
            _make_row("H1", "Prod A", "V1", "100", "50", seller_discount="40"),
            _make_row("H2", "Prod B", "V1", "100", "50", seller_discount="40"),
        ])
        assert high_flag.details["fake_discount_flag"] is True

        mixed_flag = calculate_discount([
            _make_row("M1", "Prod A", "V1", "100", "50", seller_discount="40"),
            _make_row("M2", "Prod B", "V1", "100", "100", seller_discount="0"),
        ])
        assert mixed_flag.details["fake_discount_flag"] is False

    def test_mnd_exact_output_text(self):
        result = calculate_discount(
            MND_DATA,
            affiliate_commission=18_000_000,
            current_month_revenue=200_000_000,
        )
        expected = (
            "% Diskon TOP SKU: 21.9%\n"
            "Range: 16.9% ~ 16.9%\n"
            "Voucher 11.4%\n"
            "Paket Diskon 2.3%\n"
            "% Komisi Afiliasi: 9.0%\n"
            "📌 Berpotensi menggunakan 'fake discount'"
        )
        assert result.output_text == expected

    def test_mnd_exact_detail_values_and_totals(self):
        result = calculate_discount(
            MND_DATA,
            affiliate_commission=18_000_000,
            current_month_revenue=200_000_000,
        )
        assert result.details["discount_pct"] == "21.9%"
        assert result.details["range_min"] == "16.9%"
        assert result.details["range_max"] == "16.9%"
        assert result.details["voucher_pct"] == "11.4%"
        assert result.details["paket_pct"] == "2.3%"
        assert result.details["affiliate_commission_pct"] == "9.0%"
        assert result.details["fake_discount_flag"] is True
        assert result.details["totals"] == {
            "sum_n": pytest.approx(193000.0),
            "sum_p": pytest.approx(882000.0),
            "sum_voucher": pytest.approx(123000.0),
            "sum_paket": pytest.approx(25000.0),
            "sum_harga_setelah_diskon": pytest.approx(1075000.0),
        }
        assert result.details["top_sku"][0]["product_name"] == "MOON DAE Nami Bag"
