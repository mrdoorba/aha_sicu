"""Discount Check Calculator — sheet-parity implementation, no I/O.

Implements the business process from the Google Sheet used by the team for
seller-funded discount / fake-discount detection, while preserving the
existing backend result contract.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from app.calculators.price_parser import _parse_price


@dataclass
class DiscountResult:
    """Structured result from the discount check calculator."""

    output_text: str
    details: dict[str, Any] = field(default_factory=dict)


def _safe_num(value: Any) -> float:
    """Coerce a value to float, treating None/'-'/'' as 0."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-"):
            return 0.0
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _roundup(value: float, decimals: int) -> float:
    factor = 10**decimals
    return math.ceil(value * factor) / factor


def _format_pct_1dp(fraction: float) -> str:
    return f"{fraction * 100:.1f}%"


def _calculate_urutan(rows: list[dict]) -> list[int]:
    """Legacy helper retained for compatibility with existing imports/tests."""
    result: list[int] = []
    prev_order = None
    counter = 0

    for row in rows:
        order_num = str(row.get("No. Pesanan", "") or "").strip()
        if not order_num:
            result.append(0)
            prev_order = None
            continue

        if order_num == prev_order:
            counter += 1
        else:
            counter = 1

        result.append(counter)
        prev_order = order_num

    return result


@dataclass
class LineItem:
    """Calculated row values aligned to the Google Sheet process."""

    order_num: str
    composite_key: str
    harga_awal: float
    harga_setelah_diskon: float
    jumlah: float
    seller_discount: float
    shopee_discount: float
    voucher: float
    cashback: float
    paket: float
    seller_discount_pct: float | None
    campaign_discount: float = 0.0
    total_paid: float = 0.0


@dataclass
class ProductSummary:
    """Aggregated product stats exposed via the stable result contract."""

    product_name: str
    qty: float
    avg_discount_pct: float


def _normalize_rows(rows: list[dict], *, marketplace: str = "ID") -> list[LineItem]:
    items: list[LineItem] = []
    for row in rows:
        order_num = str(row.get("No. Pesanan", "") or "").strip()
        product_name = str(row.get("Nama Produk", "") or "").strip()
        variant_name = str(row.get("Nama Variasi", "") or "").strip()
        composite_key = f"{product_name}{variant_name}".strip()

        harga_awal = _parse_price(row.get("Harga Awal"), marketplace)
        harga_setelah_diskon = _parse_price(row.get("Harga Setelah Diskon"), marketplace)
        jumlah = _safe_num(row.get("Jumlah"))
        seller_discount = _parse_price(row.get("Diskon Dari Penjual"), marketplace)
        shopee_discount = _parse_price(row.get("Diskon Dari Shopee"), marketplace)
        voucher = _parse_price(row.get("Voucher Ditanggung Penjual"), marketplace)
        cashback = _parse_price(row.get("Cashback Koin") or row.get("Cashback Coin"), marketplace)
        paket = _parse_price(
            row.get("Paket Diskon (Diskon dari Penjual)") or row.get("Paket Diskon"),
            marketplace,
        )

        seller_discount_pct: float | None = None
        if seller_discount > 0 and harga_awal > 0 and harga_setelah_diskon > 0 and jumlah > 0:
            seller_discount_pct = (seller_discount / jumlah) / harga_awal

        items.append(
            LineItem(
                order_num=order_num,
                composite_key=composite_key,
                harga_awal=harga_awal,
                harga_setelah_diskon=harga_setelah_diskon,
                jumlah=jumlah,
                seller_discount=seller_discount,
                shopee_discount=shopee_discount,
                voucher=voucher,
                cashback=cashback,
                paket=paket,
                seller_discount_pct=seller_discount_pct,
            )
        )

    return items


def _compute_fake_discount_gate(items: list[LineItem]) -> bool:
    values = [item.seller_discount_pct for item in items if item.seller_discount_pct is not None]
    if not values:
        return False
    return (sum(values) / len(values)) > 0.20


def _build_reference_price_map(
    items: list[LineItem],
    *,
    fake_discount_gate: bool,
) -> dict[str, float]:
    values_by_key: dict[str, list[float]] = defaultdict(list)

    for item in items:
        if not item.composite_key:
            continue

        value = item.harga_setelah_diskon if fake_discount_gate else item.harga_awal
        if value != 0:
            values_by_key[item.composite_key].append(value)

    reference_price_by_key: dict[str, float] = {}
    for key, values in values_by_key.items():
        median_value = statistics.median(values)
        upper_bound = median_value * 1.4
        filtered = [value for value in values if value <= upper_bound]
        reference_price_by_key[key] = max(filtered) if filtered else 0.0

    return reference_price_by_key


def _apply_sheet_metrics(items: list[LineItem], *, fake_discount_gate: bool) -> list[LineItem]:
    reference_price_by_key = _build_reference_price_map(items, fake_discount_gate=fake_discount_gate)
    order_counts = Counter(item.order_num for item in items if item.order_num)
    first_by_order: dict[str, LineItem] = {}
    for item in items:
        if item.order_num and item.order_num not in first_by_order:
            first_by_order[item.order_num] = item

    for item in items:
        if not item.composite_key:
            item.campaign_discount = 0.0
            item.total_paid = 0.0
            continue

        reference_price = reference_price_by_key.get(item.composite_key, 0.0)
        order_count = order_counts.get(item.order_num, 0)
        order_anchor = first_by_order.get(item.order_num)
        voucher_alloc = (order_anchor.voucher / order_count) if order_anchor and order_count else 0.0
        paket_alloc = (order_anchor.paket / order_count) if order_anchor and order_count else 0.0
        cashback_alloc = (order_anchor.cashback / order_count) if order_anchor and order_count else 0.0
        shopee_component = (item.shopee_discount / item.jumlah) if item.jumlah > 0 else 0.0

        gate_base = item.harga_setelah_diskon if fake_discount_gate else item.harga_awal
        adjustment = 0.0
        if gate_base > 0:
            adjustment = (
                -(item.harga_setelah_diskon * item.jumlah)
                + voucher_alloc
                + paket_alloc
                - cashback_alloc
                - shopee_component
            )
        item.campaign_discount = (reference_price * item.jumlah) + adjustment

        if item.harga_setelah_diskon <= 0:
            item.total_paid = 0.0
        else:
            paid_base = item.harga_setelah_diskon if fake_discount_gate else item.harga_awal
            item.total_paid = paid_base - item.campaign_discount

    return items


def _calculate_line_items(
    rows: list[dict],
    urutan_list: list[int],
    *,
    marketplace: str = "ID",
) -> list[LineItem]:
    """Legacy entry point retained for compatibility; now returns sheet-parity rows."""
    del urutan_list
    items = _normalize_rows(rows, marketplace=marketplace)
    fake_discount_gate = _compute_fake_discount_gate(items)
    return _apply_sheet_metrics(items, fake_discount_gate=fake_discount_gate)


def _build_product_summary(line_items: list[LineItem]) -> list[ProductSummary]:
    ordered_keys: list[str] = []
    seen: set[str] = set()
    for item in line_items:
        if item.composite_key and item.harga_setelah_diskon != 0 and item.composite_key not in seen:
            seen.add(item.composite_key)
            ordered_keys.append(item.composite_key)

    summaries: list[ProductSummary] = []
    for key in ordered_keys:
        grouped = [item for item in line_items if item.composite_key == key]
        qty = sum(item.jumlah for item in grouped)
        denominator = sum(item.harga_setelah_diskon for item in grouped)
        avg_discount_pct = (
            sum(item.campaign_discount for item in grouped) / denominator if denominator else 0.0
        )
        summaries.append(ProductSummary(product_name=key, qty=qty, avg_discount_pct=avg_discount_pct))

    return summaries


def _filter_top_sku(product_summary: list[ProductSummary]) -> list[ProductSummary]:
    if not product_summary:
        return []

    avg_qty = sum(item.qty for item in product_summary) / len(product_summary)
    filtered = [
        item
        for item in product_summary
        if item.qty > avg_qty and 0 < item.avg_discount_pct < 1.0
    ]
    filtered.sort(key=lambda item: item.qty, reverse=True)
    limit = round(len(product_summary) * 0.20)
    return filtered[:limit]


def _first_value_per_order(items: list[LineItem], attr: str) -> float:
    seen: set[str] = set()
    total = 0.0
    for item in items:
        if item.order_num and item.order_num not in seen:
            seen.add(item.order_num)
            total += float(getattr(item, attr))
    return total


def _format_output(
    line_items: list[LineItem],
    top_sku: list[ProductSummary],
) -> tuple[str, dict[str, Any]]:
    discount_pct_numerator = sum(item.campaign_discount for item in line_items if item.total_paid > 0)
    sum_total_paid = sum(item.total_paid for item in line_items)
    discount_pct = discount_pct_numerator / sum_total_paid if sum_total_paid else 0.0

    top_discount_values = [item.avg_discount_pct for item in top_sku]
    if top_discount_values:
        range_min = _roundup(min(top_discount_values), 3)
        range_max = _roundup(max(top_discount_values), 3)
    else:
        range_min = 0.0
        range_max = 0.0

    sum_voucher = _first_value_per_order(line_items, "voucher")
    sum_paket = _first_value_per_order(line_items, "paket")
    sum_harga_setelah_diskon = sum(item.harga_setelah_diskon for item in line_items)
    voucher_pct = sum_voucher / sum_harga_setelah_diskon if sum_harga_setelah_diskon else 0.0
    paket_pct = sum_paket / sum_harga_setelah_diskon if sum_harga_setelah_diskon else 0.0

    fake_discount_flag = _compute_fake_discount_gate(line_items)

    output1 = f"% Diskon TOP SKU: {_format_pct_1dp(discount_pct)}"
    output2 = f"Range: {_format_pct_1dp(range_min)} ~ {_format_pct_1dp(range_max)}"
    output3 = f"Voucher {_format_pct_1dp(voucher_pct)}"
    output4 = f"Paket Diskon {_format_pct_1dp(paket_pct)}"
    output5 = "📌 Berpotensi menggunakan 'fake discount'" if fake_discount_flag else ""

    lines = [output1, output2, output3, output4]
    if output5:
        lines.append(output5)
    output_text = "\n".join(lines)

    formatted_discount_pct = _format_pct_1dp(discount_pct)
    formatted_range_min = _format_pct_1dp(range_min)
    formatted_range_max = _format_pct_1dp(range_max)
    formatted_voucher_pct = _format_pct_1dp(voucher_pct)
    formatted_paket_pct = _format_pct_1dp(paket_pct)

    i18n: dict[str, Any] = {
        "topSkuDiscount": {"key": "discount.output.topSkuDiscount", "vars": {"value": formatted_discount_pct}},
        "range": {"key": "discount.output.range", "vars": {"min": formatted_range_min, "max": formatted_range_max}},
        "voucher": {"key": "discount.output.voucher", "vars": {"value": formatted_voucher_pct}},
        "packageDiscount": {"key": "discount.output.packageDiscount", "vars": {"value": formatted_paket_pct}},
    }
    if fake_discount_flag:
        i18n["fakeDiscount"] = {"key": "discount.output.fakeDiscount", "vars": {}}

    details = {
        "discount_pct": formatted_discount_pct,
        "range_min": formatted_range_min,
        "range_max": formatted_range_max,
        "voucher_pct": formatted_voucher_pct,
        "paket_pct": formatted_paket_pct,
        "discount_pct_raw": discount_pct,
        "range_min_raw": range_min,
        "range_max_raw": range_max,
        "voucher_pct_raw": voucher_pct,
        "paket_pct_raw": paket_pct,
        "fake_discount_flag": fake_discount_flag,
        "i18n": i18n,
        "totals": {
            "sum_n": sum(item.campaign_discount for item in line_items),
            "sum_p": sum_total_paid,
            "sum_voucher": sum_voucher,
            "sum_paket": sum_paket,
            "sum_harga_setelah_diskon": sum_harga_setelah_diskon,
        },
    }

    return output_text, details


def _empty_result() -> DiscountResult:
    return DiscountResult(
        output_text="% Diskon TOP SKU: 0.0%\nRange: 0.0% ~ 0.0%\nVoucher 0.0%\nPaket Diskon 0.0%",
        details={
            "discount_pct": "0.0%",
            "range_min": "0.0%",
            "range_max": "0.0%",
            "voucher_pct": "0.0%",
            "paket_pct": "0.0%",
            "discount_pct_raw": 0.0,
            "range_min_raw": 0.0,
            "range_max_raw": 0.0,
            "voucher_pct_raw": 0.0,
            "paket_pct_raw": 0.0,
            "fake_discount_flag": False,
            "i18n": {
                "topSkuDiscount": {"key": "discount.output.topSkuDiscount", "vars": {"value": "0.0%"}},
                "range": {"key": "discount.output.range", "vars": {"min": "0.0%", "max": "0.0%"}},
                "voucher": {"key": "discount.output.voucher", "vars": {"value": "0.0%"}},
                "packageDiscount": {"key": "discount.output.packageDiscount", "vars": {"value": "0.0%"}},
            },
            "product_summary": [],
            "top_sku": [],
            "totals": {
                "sum_n": 0.0,
                "sum_p": 0.0,
                "sum_voucher": 0.0,
                "sum_paket": 0.0,
                "sum_harga_setelah_diskon": 0.0,
            },
        },
    )


def calculate_discount(
    order_data: list[dict],
    *,
    marketplace: str = "ID",
) -> DiscountResult:
    """Execute the Discount Check Calculator using the sheet-parity process."""
    if not order_data:
        return _empty_result()

    urutan_list = _calculate_urutan(order_data)
    line_items = _calculate_line_items(order_data, urutan_list, marketplace=marketplace)
    product_summary = _build_product_summary(line_items)
    top_sku = _filter_top_sku(product_summary)
    output_text, details = _format_output(line_items, top_sku)

    details["product_summary"] = [
        {
            "product_name": item.product_name,
            "qty": item.qty,
            "avg_discount_pct": item.avg_discount_pct,
        }
        for item in product_summary
    ]
    details["top_sku"] = [
        {
            "product_name": item.product_name,
            "qty": item.qty,
            "avg_discount_pct": item.avg_discount_pct,
        }
        for item in top_sku
    ]

    return DiscountResult(output_text=output_text, details=details)
