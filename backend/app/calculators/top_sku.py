"""Top SKU Calculator — pure function, no I/O.

Processes Order Export and Mass Update data to find top-selling
products with revenue and stock analysis.

Spec: logic/calculator-2-penjualan.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.calculators.price_parser import _parse_price
from app.calculators.scoring.helpers import _safe_num


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class TopSkuResult:
    """Structured result from the top SKU calculator."""

    output_text: str
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------

@dataclass
class LineItem:
    """Per-line extracted data from order export."""

    sku: str
    product_variant_label: str
    quantity: float
    revenue: float


def _extract_per_line(rows: list[dict], *, marketplace: str = "ID") -> list[LineItem]:
    """Extract per-line data from order export rows.

    Revenue = (Harga Setelah Diskon × Jumlah)
              - (Voucher Ditanggung Penjual / Jumlah Produk di Pesan)
              - (Cashback Koin / Jumlah Produk di Pesan)
              + (Diskon dari Shopee / Jumlah Produk di Pesan)
    """
    items: list[LineItem] = []

    for row in rows:
        sku = str(row.get("Nomor Referensi SKU", "") or "").strip()
        nama_produk = str(row.get("Nama Produk", "") or "").strip()
        nama_variasi = str(row.get("Nama Variasi", "") or "").strip()
        product_variant_label = f"{nama_produk} - {nama_variasi}"

        harga_setelah_diskon = _parse_price(row.get("Harga Setelah Diskon"), marketplace)
        jumlah = _safe_num(row.get("Jumlah"))
        jumlah_produk_di_pesan = _safe_num(row.get("Jumlah Produk di Pesan"))
        voucher = _parse_price(row.get("Voucher Ditanggung Penjual"), marketplace)
        cashback = _parse_price(row.get("Cashback Koin"), marketplace)
        diskon_shopee = _parse_price(row.get("Diskon Dari Shopee"), marketplace)

        # Avoid division by zero
        items_in_order = jumlah_produk_di_pesan if jumlah_produk_di_pesan > 0 else 1.0

        revenue = (
            (harga_setelah_diskon * jumlah)
            - (voucher / items_in_order)
            - (cashback / items_in_order)
            + (diskon_shopee / items_in_order)
        )

        items.append(LineItem(
            sku=sku,
            product_variant_label=product_variant_label,
            quantity=jumlah,
            revenue=revenue,
        ))

    return items


@dataclass
class AggregatedProduct:
    """Aggregated product stats by product+variant label."""

    product_variant_label: str
    total_qty: float
    total_omzet: float


def _aggregate_by_product(line_items: list[LineItem]) -> list[AggregatedProduct]:
    """Group by product+variant label, sum qty and revenue."""
    groups: dict[str, dict[str, float]] = {}

    for item in line_items:
        label = item.product_variant_label
        if label not in groups:
            groups[label] = {"qty": 0.0, "omzet": 0.0}
        groups[label]["qty"] += item.quantity
        groups[label]["omzet"] += item.revenue

    return [
        AggregatedProduct(
            product_variant_label=label,
            total_qty=data["qty"],
            total_omzet=data["omzet"],
        )
        for label, data in groups.items()
    ]


def _rank_top_products(
    aggregated: list[AggregatedProduct],
) -> list[AggregatedProduct]:
    """Sort by omzet descending, limit = MAX(ROUND(unique × 20%), 20).

    If fewer than 20 unique products, return all.
    """
    if not aggregated:
        return []

    sorted_products = sorted(aggregated, key=lambda p: p.total_omzet, reverse=True)
    unique_count = len(sorted_products)

    if unique_count <= 20:
        return sorted_products

    limit = max(round(unique_count * 0.20), 20)
    return sorted_products[:limit]


def _build_mass_update_lookup(
    mass_update_data: list[dict],
) -> tuple[dict[str, str], dict[str, int]]:
    """Build lookup dicts from mass update data.

    Returns:
        (name_to_kode, kode_to_stok):
        - name_to_kode: "Nama Produk - Nama Variasi" → Kode Variasi
        - kode_to_stok: Kode Variasi → Stok
    """
    name_to_kode: dict[str, str] = {}
    kode_to_stok: dict[str, int] = {}

    for row in mass_update_data:
        nama_produk = str(row.get("Nama Produk", "") or "").strip()
        nama_variasi = str(row.get("Nama Variasi", "") or "").strip()
        kode_variasi = str(row.get("Kode Variasi", "") or "").strip()
        stok_keys = [k for k in row if isinstance(k, str) and k.startswith("Stok")]
        stok = int(sum(_safe_num(row.get(k)) for k in stok_keys)) if stok_keys else 0

        label = f"{nama_produk} - {nama_variasi}"
        if kode_variasi:
            if label not in name_to_kode:
                name_to_kode[label] = kode_variasi
            kode_to_stok[kode_variasi] = stok

    return name_to_kode, kode_to_stok


@dataclass
class EnrichedProduct:
    """Top product enriched with mass update data."""

    product_variant_label: str
    total_qty: float
    total_omzet: float
    kode_variasi: str
    rata2_harga_jual: float
    stok: int


def _enrich_with_mass_update(
    top_products: list[AggregatedProduct],
    line_items: list[LineItem],
    mu_lookup: tuple[dict[str, str], dict[str, int]],
) -> list[EnrichedProduct]:
    """Enrich top products with kode_variasi, rata2_harga_jual, stok."""
    name_to_kode, kode_to_stok = mu_lookup

    # Pre-compute max revenue per product+variant label
    max_revenue: dict[str, float] = {}
    for item in line_items:
        label = item.product_variant_label
        if label not in max_revenue or item.revenue > max_revenue[label]:
            max_revenue[label] = item.revenue

    enriched: list[EnrichedProduct] = []
    for product in top_products:
        label = product.product_variant_label

        # Kode Variasi lookup
        kode = name_to_kode.get(label, "Kode Variasi tidak ditemukan")

        # Rata2 Harga Jual = max single-line revenue
        rata2 = max_revenue.get(label, 0.0)

        # Stock lookup
        if kode == "Kode Variasi tidak ditemukan":
            stok = 0
        else:
            stok = kode_to_stok.get(kode, 0)

        enriched.append(EnrichedProduct(
            product_variant_label=label,
            total_qty=product.total_qty,
            total_omzet=product.total_omzet,
            kode_variasi=kode,
            rata2_harga_jual=rata2,
            stok=stok,
        ))

    return enriched


def _build_output_tables(
    enriched_products: list[EnrichedProduct],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Generate output_1 and output_2 table structures.

    Output 1: kode_variasi, product_name, total_omzet, rata2_harga_jual
    Output 2: kode_variasi, nama_produk (without variant), varian, stok
    """
    output_1: list[dict[str, Any]] = []
    output_2: list[dict[str, Any]] = []

    for product in enriched_products:
        # Output 1
        output_1.append({
            "kode_variasi": product.kode_variasi,
            "product_name": product.product_variant_label,
            "total_omzet": round(product.total_omzet),
            "rata2_harga_jual": round(product.rata2_harga_jual),
        })

        # Output 2: split product_variant_label into nama_produk and varian
        parts = product.product_variant_label.rsplit(" - ", 1)
        nama_produk = parts[0].strip() if parts else ""
        varian = parts[1].strip() if len(parts) > 1 else ""

        output_2.append({
            "kode_variasi": product.kode_variasi,
            "nama_produk": nama_produk,
            "varian": varian,
            "stok": product.stok,
        })

    return output_1, output_2


def _calculate_average_stock(enriched_products: list[EnrichedProduct]) -> int:
    """ROUND(AVERAGE(stock of all top products)) — integer."""
    if not enriched_products:
        return 0
    total_stok = sum(p.stok for p in enriched_products)
    return round(total_stok / len(enriched_products))


def _calculate_out_of_stock_pct(enriched_products: list[EnrichedProduct]) -> float:
    """Fraction of top products with stock == 0: 0.0–1.0."""
    if not enriched_products:
        return 0.0
    out_count = sum(1 for p in enriched_products if p.stok == 0)
    return round(out_count / len(enriched_products), 2)


# ---------------------------------------------------------------------------
# Main calculator entry point
# ---------------------------------------------------------------------------

def calculate_top_sku(
    order_data: list[dict],
    mass_update_data: list[dict],
    *,
    marketplace: str = "ID",
) -> TopSkuResult:
    """Execute the Top SKU Calculator.

    Pure function — no I/O, no database access.

    Args:
        order_data: Parsed rows from order_export (list of dicts).
        mass_update_data: Parsed rows from mass_update (list of dicts).
        marketplace: ``"ID"`` (Indonesian) or ``"TH"`` (Thai) price format.

    Returns:
        TopSkuResult with output_text and details.
    """
    if not order_data:
        return TopSkuResult(
            output_text="",
            details={
                "output_1": [],
                "output_2": [],
                "average_stock": 0,
                "out_of_stock_pct": 0.0,
                "product_count": 0,
                "total_unique_products": 0,
            },
        )

    # Step 1: Extract per-line data
    line_items = _extract_per_line(order_data, marketplace=marketplace)

    # Step 2: Aggregate by product+variant
    aggregated = _aggregate_by_product(line_items)
    total_unique = len(aggregated)

    # Step 3: Rank top products
    top_products = _rank_top_products(aggregated)

    # Step 4-6: Build mass update lookup and enrich
    mu_lookup = _build_mass_update_lookup(mass_update_data)
    enriched = _enrich_with_mass_update(top_products, line_items, mu_lookup)

    # Step 7: Average stock
    average_stock = _calculate_average_stock(enriched)

    # Step 7b: Out-of-stock percentage
    out_of_stock_pct = _calculate_out_of_stock_pct(enriched)

    # Step 8: Build output tables
    output_1, output_2 = _build_output_tables(enriched)

    return TopSkuResult(
        output_text="",
        details={
            "output_1": output_1,
            "output_2": output_2,
            "average_stock": average_stock,
            "out_of_stock_pct": out_of_stock_pct,
            "product_count": len(enriched),
            "total_unique_products": total_unique,
        },
    )
