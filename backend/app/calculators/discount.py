"""Discount Check Calculator — pure function, no I/O.

Processes Order Export data to analyze discount patterns
and detect potential fake discounts.

Spec: logic/calculator-3-discount-checkup.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class DiscountResult:
    """Structured result from the discount check calculator."""

    output_text: str
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _clean_price(value: Any) -> float:
    """Remove '.' thousands separator and convert to number.

    Indonesian price format: '125.000' → 125000, '1.250.000' → 1250000.
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return 0.0
    s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------

def _calculate_urutan(rows: list[dict]) -> list[int]:
    """Compute item position (Urutan) within each order.

    Same order number as previous row → increment.
    Different order number → reset to 1.
    Empty order number → 0 (skip).
    """
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
    """Calculated values for a single order line."""

    harga_awal: float
    harga_setelah_diskon: float
    voucher: float
    paket: float
    jumlah: float
    nama_produk: str
    total_discount: float  # N
    discount_pct: float    # O
    total_paid: float      # P
    urutan: int


def _calculate_line_items(rows: list[dict], urutan_list: list[int]) -> list[LineItem]:
    """Compute N (total discount), O (discount %), P (total paid) per line."""
    items: list[LineItem] = []

    for row, urutan in zip(rows, urutan_list):
        if urutan == 0:
            continue

        harga_awal = _clean_price(row.get("Harga Awal"))
        harga_setelah_diskon = _clean_price(row.get("Harga Setelah Diskon"))
        jumlah = _safe_num(row.get("Jumlah"))
        nama_produk = str(row.get("Nama Produk", "") or "").strip()

        # Voucher and Paket only applied at Urutan=1
        if urutan == 1:
            voucher = _clean_price(row.get("Voucher Ditanggung Penjual"))
            paket = _clean_price(row.get("Paket Diskon (Diskon dari Penjual)"))
        else:
            voucher = 0.0
            paket = 0.0

        # N = (Harga Awal - Harga Setelah Diskon) + Voucher + Paket
        total_discount = (harga_awal - harga_setelah_diskon) + voucher + paket

        # O = N / Harga Awal
        discount_pct = total_discount / harga_awal if harga_awal > 0 else 0.0

        # P = Harga Setelah Diskon - Voucher - Paket
        total_paid = harga_setelah_diskon - voucher - paket

        items.append(LineItem(
            harga_awal=harga_awal,
            harga_setelah_diskon=harga_setelah_diskon,
            voucher=voucher,
            paket=paket,
            jumlah=jumlah,
            nama_produk=nama_produk,
            total_discount=total_discount,
            discount_pct=discount_pct,
            total_paid=total_paid,
            urutan=urutan,
        ))

    return items


@dataclass
class ProductSummary:
    """Aggregated product stats."""

    product_name: str
    qty: float
    avg_discount_pct: float


def _build_product_summary(line_items: list[LineItem]) -> list[ProductSummary]:
    """Group by Nama Produk (exact match), aggregate qty and avg discount %."""
    groups: dict[str, dict[str, Any]] = {}

    for item in line_items:
        name = item.nama_produk
        if not name:
            continue

        if name not in groups:
            groups[name] = {"qty": 0.0, "disc_values": []}

        groups[name]["qty"] += item.jumlah
        groups[name]["disc_values"].append(item.discount_pct)

    summaries: list[ProductSummary] = []
    for name, data in groups.items():
        disc_values = data["disc_values"]
        avg_disc = sum(disc_values) / len(disc_values) if disc_values else 0.0
        summaries.append(ProductSummary(
            product_name=name,
            qty=data["qty"],
            avg_discount_pct=avg_disc,
        ))

    return summaries


def _filter_top_sku(product_summary: list[ProductSummary]) -> list[ProductSummary]:
    """Filter TOP SKU: qty > avg AND avg_disc < 1.0, limit ROUND(unique * 20%).

    Order by qty descending. No minimum floor (differs from Calculator 2).
    """
    if not product_summary:
        return []

    avg_qty = sum(p.qty for p in product_summary) / len(product_summary)

    # Filter: qty > average AND avg_disc < 1.0 (100%)
    filtered = [
        p for p in product_summary
        if p.qty > avg_qty and p.avg_discount_pct < 1.0
    ]

    # Order by qty descending
    filtered.sort(key=lambda p: p.qty, reverse=True)

    # Limit = ROUND(unique_products * 20%)
    unique_count = len(product_summary)
    limit = round(unique_count * 0.20)

    return filtered[:limit]


def _roundup(value: float, decimals: int) -> float:
    """Round UP to specified decimal places.

    math.ceil works on integers — for decimal places:
    math.ceil(value * 10^decimals) / 10^decimals
    """
    factor = 10 ** decimals
    return math.ceil(value * factor) / factor


def _format_pct_1dp(fraction: float) -> str:
    """Format fraction as percentage with 1 decimal place: 0.027 → '2.7%'."""
    return f"{fraction * 100:.1f}%"


def _format_output(
    line_items: list[LineItem],
    top_sku: list[ProductSummary],
) -> tuple[str, dict[str, Any]]:
    """Generate the 5 output values as formatted text.

    Returns (output_text, details_dict).
    """
    sum_n = sum(item.total_discount for item in line_items)
    sum_p = sum(item.total_paid for item in line_items)
    sum_voucher = sum(item.voucher for item in line_items)
    sum_paket = sum(item.paket for item in line_items)
    sum_harga_setelah_diskon = sum(item.harga_setelah_diskon for item in line_items)

    # Output 1: % Diskon TOP SKU = SUMIF(P>0, N) / SUM(P)
    sum_n_where_p_positive = sum(
        item.total_discount for item in line_items if item.total_paid > 0
    )
    discount_pct = sum_n_where_p_positive / sum_p if sum_p != 0 else 0.0
    output1 = f"% Diskon TOP SKU: {_format_pct_1dp(discount_pct)}"

    # Output 2: Range = ROUNDUP(MIN(top_sku_avg_disc), 3) ~ ROUNDUP(MAX(top_sku_avg_disc), 3)
    if top_sku:
        top_disc_values = [p.avg_discount_pct for p in top_sku]
        range_min = _roundup(min(top_disc_values), 3)
        range_max = _roundup(max(top_disc_values), 3)
    else:
        range_min = 0.0
        range_max = 0.0
    output2 = f"Range: {_format_pct_1dp(range_min)} ~ {_format_pct_1dp(range_max)}"

    # Output 3: Voucher % = SUM(voucher) / SUM(harga_setelah_diskon)
    voucher_pct = sum_voucher / sum_harga_setelah_diskon if sum_harga_setelah_diskon != 0 else 0.0
    output3 = f"Voucher {_format_pct_1dp(voucher_pct)}"

    # Output 4: Paket Diskon % = SUM(paket) / SUM(harga_setelah_diskon)
    paket_pct = sum_paket / sum_harga_setelah_diskon if sum_harga_setelah_diskon != 0 else 0.0
    output4 = f"Paket Diskon {_format_pct_1dp(paket_pct)}"

    # Output 5: Fake Discount Flag
    fake_discount_ratio = sum_n / sum_p if sum_p != 0 else 0.0
    fake_discount_flag = fake_discount_ratio > 0.20
    output5 = "📌 Berpotensi menggunakan 'fake discount'" if fake_discount_flag else ""

    # Combine output
    lines = [output1, output2, output3, output4]
    if output5:
        lines.append(output5)
    output_text = "\n".join(lines)

    details = {
        "discount_pct": _format_pct_1dp(discount_pct),
        "range_min": _format_pct_1dp(range_min),
        "range_max": _format_pct_1dp(range_max),
        "voucher_pct": _format_pct_1dp(voucher_pct),
        "paket_pct": _format_pct_1dp(paket_pct),
        "fake_discount_flag": fake_discount_flag,
        "totals": {
            "sum_n": sum_n,
            "sum_p": sum_p,
            "sum_voucher": sum_voucher,
            "sum_paket": sum_paket,
            "sum_harga_setelah_diskon": sum_harga_setelah_diskon,
        },
    }

    return output_text, details


# ---------------------------------------------------------------------------
# Main calculator entry point
# ---------------------------------------------------------------------------

def calculate_discount(order_data: list[dict]) -> DiscountResult:
    """Execute the Discount Check Calculator.

    Pure function — no I/O, no database access.

    Args:
        order_data: Parsed rows from order_export (list of dicts).

    Returns:
        DiscountResult with output_text and details.
    """
    if not order_data:
        return DiscountResult(
            output_text="% Diskon TOP SKU: 0.0%\nRange: 0.0% ~ 0.0%\nVoucher 0.0%\nPaket Diskon 0.0%",
            details={
                "discount_pct": "0.0%",
                "range_min": "0.0%",
                "range_max": "0.0%",
                "voucher_pct": "0.0%",
                "paket_pct": "0.0%",
                "fake_discount_flag": False,
                "product_summary": [],
                "top_sku": [],
                "totals": {
                    "sum_n": 0,
                    "sum_p": 0,
                    "sum_voucher": 0,
                    "sum_paket": 0,
                    "sum_harga_setelah_diskon": 0,
                },
            },
        )

    # Step 1: Calculate Urutan
    urutan_list = _calculate_urutan(order_data)

    # Steps 2-6: Calculate line items (clean prices, apply voucher/paket, compute N/O/P)
    line_items = _calculate_line_items(order_data, urutan_list)

    # Step 7: Product summary
    product_summary = _build_product_summary(line_items)

    # Step 8: TOP SKU filter
    top_sku = _filter_top_sku(product_summary)

    # Generate output
    output_text, details = _format_output(line_items, top_sku)

    # Add product_summary and top_sku to details
    details["product_summary"] = [
        {
            "product_name": p.product_name,
            "qty": p.qty,
            "avg_discount_pct": p.avg_discount_pct,
        }
        for p in product_summary
    ]
    details["top_sku"] = [
        {
            "product_name": p.product_name,
            "qty": p.qty,
            "avg_discount_pct": p.avg_discount_pct,
        }
        for p in top_sku
    ]

    return DiscountResult(output_text=output_text, details=details)
