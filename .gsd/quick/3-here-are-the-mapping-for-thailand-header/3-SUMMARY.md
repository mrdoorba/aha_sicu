# Quick Task: Thai order export header mapping + synthetic column

**Date:** 2026-03-17
**Branch:** gsd/quick/3-here-are-the-mapping-for-thailand-header

## What Changed
- Added `_normalise_thai_columns()` in `parser.py` — renames 11 Thai Shopee order export column headers to Indonesian equivalents
- Computes synthetic `Jumlah Produk di Pesan` column (count of rows per `No. Pesanan`) since Thai exports don't include it
- Wired normalisation into `_parse_file()` in `service.py` — runs after parsing, before column validation
- Sets `source_language = "th"` when Thai headers detected
- 7 new tests: column rename, synthetic column (multi-item order, single-item, 5-item), validation pass-through, Indonesian passthrough, no-overwrite guard

## Column Mapping
| Thai | Indonesian |
|---|---|
| หมายเลขคำสั่งซื้อ | No. Pesanan |
| ชื่อสินค้า | Nama Produk |
| ราคาตั้งต้น | Harga Awal |
| ราคาขาย | Harga Setelah Diskon |
| จำนวน | Jumlah |
| โค้ดส่วนลดชำระโดยผู้ขาย | Voucher Ditanggung Penjual |
| ส่วนลด bundle deal ชำระโดยผู้ขาย | Paket Diskon (Diskon dari Penjual) |
| เลขอ้างอิง SKU (SKU Reference No.) | Nomor Referensi SKU |
| ชื่อตัวเลือก | Nama Variasi |
| โค้ด Coins Cashback ชำระโดยผู้ขาย | Cashback Koin |
| ส่วนลดจาก Shopee | Diskon Dari Shopee |
| *(computed: row count per order)* | Jumlah Produk di Pesan |

## Files Modified
- `backend/app/modules/upload/parser.py` — `_ORDER_EXPORT_COLUMN_RENAME_TH` dict + `_normalise_thai_columns()` function
- `backend/app/modules/upload/service.py` — import + call in `_parse_file()`
- `backend/tests/unit/test_parser.py` — 7 new tests in `TestThaiOrderExportNormalisation`

## Verification
- 1082 backend tests pass (1075 existing + 7 new)
- All 26 parser tests pass
