#!/usr/bin/env python3
# ruff: noqa: E402
"""Create a Google-Sheets-importable workbook for the discount calculator.

This script loads a Shopee order export (ZIP or Excel), normalises it using the
same upload/parsing layer as the backend, runs the current discount calculator
logic, and writes an .xlsx workbook that can be uploaded into Google Sheets.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import xlsxwriter
from app.calculators.discount import (  # type: ignore[import-not-found]
    _apply_sheet_metrics,
    _build_product_summary,
    _build_reference_price_map,
    _compute_fake_discount_gate,
    _filter_top_sku,
    _normalize_rows,
    calculate_discount,
)
from app.modules.upload.parser import (  # type: ignore[import-not-found]
    REQUIRED_COLUMNS,
    _normalise_english_columns,
    _normalise_thai_columns,
    parse_excel,
    validate_columns,
)
from app.modules.upload.zip_handler import process_zip  # type: ignore[import-not-found]


INPUT_COLUMNS = REQUIRED_COLUMNS["order_export"]
SUMMARY_METRICS = [
    ("Discount TOP SKU", "discount_pct"),
    ("Range min", "range_min"),
    ("Range max", "range_max"),
    ("Voucher %", "voucher_pct"),
    ("Paket Diskon %", "paket_pct"),
]
TOTAL_KEYS = [
    ("Sum campaign discount", "sum_n"),
    ("Sum total paid", "sum_p"),
    ("Sum voucher", "sum_voucher"),
    ("Sum paket", "sum_paket"),
    ("Sum harga setelah diskon", "sum_harga_setelah_diskon"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an .xlsx workbook that mirrors the current discount "
            "calculator output and can be imported into Google Sheets."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to an order export .zip/.xlsx/.xls file.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output .xlsx path.",
    )
    return parser.parse_args()


def _load_order_export(path: Path) -> tuple[Any, Any, str, str]:
    file_bytes = path.read_bytes()
    suffix = path.suffix.lower()

    if suffix == ".zip":
        source_df = process_zip(file_bytes, "order_export")
    elif suffix in {".xlsx", ".xls"}:
        source_df = parse_excel(file_bytes, header_row=0)
    else:
        raise SystemExit(f"Unsupported input type: {path.name}")

    normalized_df = source_df.clone()
    normalized_df, was_english = _normalise_english_columns(normalized_df)
    normalized_df, was_thai = _normalise_thai_columns(normalized_df)
    validate_columns(normalized_df, "order_export")

    source_language = "th" if was_thai else "en" if was_english else "id"
    marketplace = "TH" if source_language == "th" else "ID"
    return source_df, normalized_df, source_language, marketplace


def _to_records(df: Any, columns: list[str] | None = None) -> list[dict[str, Any]]:
    if columns is not None:
        df = df.select(columns)
    return [dict(row) for row in df.iter_rows(named=True)]


def _safe_cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool, datetime, date)):
        return value
    return str(value)


def _line_item_records(order_rows: list[dict[str, Any]], marketplace: str) -> tuple[list[dict[str, Any]], bool]:
    items = _normalize_rows(order_rows, marketplace=marketplace)
    fake_discount_gate = _compute_fake_discount_gate(items)
    reference_price_by_key = _build_reference_price_map(items, fake_discount_gate=fake_discount_gate)
    order_counts = Counter(item.order_num for item in items if item.order_num)

    first_by_order: dict[str, Any] = {}
    for item in items:
        if item.order_num and item.order_num not in first_by_order:
            first_by_order[item.order_num] = item

    _apply_sheet_metrics(items, fake_discount_gate=fake_discount_gate)

    records: list[dict[str, Any]] = []
    for source_row, item in zip(order_rows, items, strict=True):
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

        records.append(
            {
                "order_num": item.order_num,
                "product_name": source_row.get("Nama Produk", ""),
                "variant_name": source_row.get("Nama Variasi", ""),
                "sku_reference": source_row.get("Nomor Referensi SKU", ""),
                "composite_key": item.composite_key,
                "harga_awal": item.harga_awal,
                "harga_setelah_diskon": item.harga_setelah_diskon,
                "jumlah": item.jumlah,
                "seller_discount": item.seller_discount,
                "shopee_discount": item.shopee_discount,
                "voucher": item.voucher,
                "cashback": item.cashback,
                "paket": item.paket,
                "seller_discount_pct": item.seller_discount_pct,
                "reference_price": reference_price_by_key.get(item.composite_key, 0.0),
                "order_row_count": order_count,
                "voucher_alloc": voucher_alloc,
                "paket_alloc": paket_alloc,
                "cashback_alloc": cashback_alloc,
                "shopee_component": shopee_component,
                "gate_base": gate_base,
                "adjustment": adjustment,
                "campaign_discount": item.campaign_discount,
                "total_paid": item.total_paid,
            }
        )

    return records, fake_discount_gate


def _product_summary_records(order_rows: list[dict[str, Any]], marketplace: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    items = _normalize_rows(order_rows, marketplace=marketplace)
    fake_discount_gate = _compute_fake_discount_gate(items)
    _apply_sheet_metrics(items, fake_discount_gate=fake_discount_gate)
    product_summary = [asdict(item) for item in _build_product_summary(items)]
    top_sku = [asdict(item) for item in _filter_top_sku(_build_product_summary(items))]
    return product_summary, top_sku


def _write_table(
    worksheet: Any,
    rows: list[dict[str, Any]],
    *,
    workbook: Any,
    percent_columns: set[str] | None = None,
    currency_columns: set[str] | None = None,
) -> None:
    percent_columns = percent_columns or set()
    currency_columns = currency_columns or set()

    header_format = workbook.add_format({
        "bold": True,
        "bg_color": "#D9EAF7",
        "border": 1,
        "text_wrap": True,
        "valign": "top",
    })
    cell_format = workbook.add_format({"valign": "top"})
    text_wrap = workbook.add_format({"text_wrap": True, "valign": "top"})
    percent_format = workbook.add_format({"num_format": "0.0%", "valign": "top"})
    money_format = workbook.add_format({"num_format": "#,##0.00", "valign": "top"})

    if not rows:
        worksheet.write(0, 0, "No rows")
        return

    columns = list(rows[0].keys())
    for col_idx, column in enumerate(columns):
        worksheet.write(0, col_idx, column, header_format)

    widths = {column: len(column) for column in columns}
    for row_idx, row in enumerate(rows, start=1):
        for col_idx, column in enumerate(columns):
            value = _safe_cell(row.get(column))
            widths[column] = min(max(widths[column], len(str(value))), 60)
            if isinstance(value, (int, float)):
                if column in percent_columns:
                    worksheet.write_number(row_idx, col_idx, float(value), percent_format)
                elif column in currency_columns:
                    worksheet.write_number(row_idx, col_idx, float(value), money_format)
                else:
                    worksheet.write_number(row_idx, col_idx, float(value), cell_format)
            else:
                fmt = text_wrap if len(str(value)) > 40 else cell_format
                worksheet.write(row_idx, col_idx, value, fmt)

    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, len(rows), len(columns) - 1)
    for col_idx, column in enumerate(columns):
        worksheet.set_column(col_idx, col_idx, min(widths[column] + 2, 60))


def _write_summary(
    workbook: Any,
    summary_rows: list[tuple[str, Any]],
    output_text: str,
) -> None:
    sheet = workbook.add_worksheet("Summary")
    title = workbook.add_format({"bold": True, "font_size": 16})
    label = workbook.add_format({"bold": True, "bg_color": "#F1F5F9", "border": 1})
    value = workbook.add_format({"border": 1})
    wrap = workbook.add_format({"border": 1, "text_wrap": True, "valign": "top"})

    sheet.write(0, 0, "Discount Calculator Workbook", title)
    sheet.set_column(0, 0, 28)
    sheet.set_column(1, 1, 50)

    for row_idx, (key, item) in enumerate(summary_rows, start=2):
        sheet.write(row_idx, 0, key, label)
        fmt = wrap if isinstance(item, str) and "\n" in item else value
        sheet.write(row_idx, 1, _safe_cell(item), fmt)

    sheet.write(len(summary_rows) + 4, 0, "Calculator output_text", label)
    sheet.write(len(summary_rows) + 4, 1, output_text, wrap)
    sheet.freeze_panes(2, 0)


def build_workbook(input_path: Path, output_path: Path) -> None:
    source_df, normalized_df, source_language, marketplace = _load_order_export(input_path)
    order_rows = _to_records(normalized_df, INPUT_COLUMNS)
    line_item_rows, fake_discount_gate = _line_item_records(order_rows, marketplace)
    product_summary_rows, top_sku_rows = _product_summary_records(order_rows, marketplace)
    result = calculate_discount(order_rows, marketplace=marketplace)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(output_path)
    try:
        summary_rows: list[tuple[str, Any]] = [
            ("Source file", str(input_path)),
            ("Generated at (UTC)", datetime.now(UTC).isoformat()),
            ("Source language", source_language),
            ("Marketplace", marketplace),
            ("Raw merged row count", source_df.height),
            ("Discount input row count", len(order_rows)),
            ("Unique product summary rows", len(product_summary_rows)),
            ("Top SKU rows", len(top_sku_rows)),
            ("Fake discount gate", fake_discount_gate),
        ]
        summary_rows.extend((label, result.details[key]) for label, key in SUMMARY_METRICS)
        summary_rows.extend((label, result.details["totals"][key]) for label, key in TOTAL_KEYS)
        _write_summary(workbook, summary_rows, result.output_text)

        source_sheet = workbook.add_worksheet("Source Orders")
        _write_table(source_sheet, _to_records(source_df), workbook=workbook)

        inputs_sheet = workbook.add_worksheet("Discount Inputs")
        _write_table(inputs_sheet, order_rows, workbook=workbook)

        line_sheet = workbook.add_worksheet("Line Items")
        _write_table(
            line_sheet,
            line_item_rows,
            workbook=workbook,
            percent_columns={"seller_discount_pct"},
            currency_columns={
                "harga_awal",
                "harga_setelah_diskon",
                "seller_discount",
                "shopee_discount",
                "voucher",
                "cashback",
                "paket",
                "reference_price",
                "voucher_alloc",
                "paket_alloc",
                "cashback_alloc",
                "shopee_component",
                "gate_base",
                "adjustment",
                "campaign_discount",
                "total_paid",
            },
        )

        product_sheet = workbook.add_worksheet("Product Summary")
        _write_table(
            product_sheet,
            product_summary_rows,
            workbook=workbook,
            percent_columns={"avg_discount_pct"},
        )

        top_sheet = workbook.add_worksheet("Top SKU")
        _write_table(
            top_sheet,
            top_sku_rows,
            workbook=workbook,
            percent_columns={"avg_discount_pct"},
        )
    finally:
        workbook.close()


def main() -> None:
    args = parse_args()
    build_workbook(args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
