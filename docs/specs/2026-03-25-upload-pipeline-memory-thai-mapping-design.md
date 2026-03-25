# Upload Pipeline: Memory Optimization & Thai Mass Update Mapping

**Date:** 2026-03-25
**Status:** Approved

## Problem

Two upload failures observed in production on 2026-03-25:

1. **Order Export OOM**: Uploading `cintage_Order.all.20260201_20260228.zip` (3.2 MB, 11K rows × 59 cols, 2-part ZIP) causes `Memory limit of 512 MiB exceeded with 547 MiB used` on Cloud Run, killing the container mid-request. The browser shows `NetworkError when attempting to fetch resource.`

2. **Mass Update missing columns**: Uploading `cintage_mass_update_sales_info_205856685_20260325150823.xlsx` (Thai Shopee export, 12,604 rows × 15 cols) fails with `Missing required columns for mass_update: Kode Produk, Kode Variasi, Nama Variasi, SKU, Harga`. No Thai→Indonesian column mapping exists for mass_update files.

## Solution

Three workstreams:

### 1. Infrastructure — Bump Cloud Run Memory

Increase `cloud_run_memory` from `512Mi` to `1Gi` in both `dev.tfvars` and `prod.tfvars`.

**Files changed:**
- `infrastructure/terraform/environments/dev.tfvars`
- `infrastructure/terraform/environments/prod.tfvars`

### 2. Processing Pipeline — Reduce Peak Memory

#### 2a. Incremental ZIP Concat

**File:** `backend/app/modules/upload/zip_handler.py`

Current code accumulates all part DataFrames in a list, then concats at the end. Peak memory: N × part_size.

Change to concat-as-you-go: each new part merges with a running result DataFrame, and the previous part becomes garbage-collectable. Peak memory: ~2 × part_size.

```python
# Before
dataframes = []
for entry in entries:
    df = parse_excel(...)
    dataframes.append(df)
return pl.concat(dataframes)

# After
result_df = None
for entry in entries:
    part_df = parse_excel(...)
    result_df = part_df if result_df is None else pl.concat([result_df, part_df])
return result_df
```

#### 2b. Columnar Storage Format for parsed_data

**File:** `backend/app/modules/upload/parser.py` (`dataframe_to_json`)

Current format uses `df.to_dicts()` — a list of dicts where every dict repeats all column names. For 59-column × 11K-row files, this creates 649K redundant key strings.

Change to list-of-lists format:

```python
# Before
{"columns": [...], "data": [{"col1": v1, "col2": v2}, ...], "row_count": N, "source_language": "id"}

# After
{"columns": [...], "rows": [[v1, v2, ...], ...], "row_count": N, "source_language": "id"}
```

**Backward compatibility:** `_extract_parsed_data` in `calculator_service.py` (line 135) is the single consumer of `parsed_data`. It is called from 5 call sites across 3 calculators (ads_keyword, discount, top_sku), all in `calculator_service.py`. It always returns `list[dict[str, Any]]`.

The updated function checks for `"rows"` key first (new format), reconstructing dicts by zipping columns with each row:

```python
if "rows" in parsed_data:
    columns = parsed_data["columns"]
    return [dict(zip(columns, row)) for row in parsed_data["rows"]]
return parsed_data.get("data", [])  # old format fallback
```

No migration needed — old uploads stored with `"data"` key continue to work. All 5 call sites receive identical `list[dict]` output regardless of storage format.

**Side benefit:** The columnar JSONB is significantly smaller on disk (no repeated key strings), helpful given Cloud SQL is on `db-f1-micro` with 10GB disk.

**Round-trip equivalence test:** Unit test verifying that reconstructed list-of-dicts from columns+rows matches `to_dicts()` output exactly.

**Files changed:**
- `backend/app/modules/upload/parser.py` — `dataframe_to_json` produces `"rows"` format
- `backend/app/modules/evaluations/calculator_service.py` — `_extract_parsed_data` reads both formats
- Tests for round-trip equivalence

### 3. Thai Mass Update Column Mapping

**File:** `backend/app/modules/upload/parser.py`

New mapping dict and normalisation function:

```python
_MASS_UPDATE_COLUMN_RENAME_TH: dict[str, str] = {
    "รหัสสินค้า": "Kode Produk",
    "ชื่อสินค้า": "Nama Produk",
    "รหัสตัวเลือกสินค้า": "Kode Variasi",
    "ชื่อตัวเลือกสินค้า": "Nama Variasi",
    "เลข SKU": "SKU",
    "ราคา": "Harga",
}
```

Stock wildcard rename (same pattern as English `Stock*` → `Stok*`):
- `คลัง` → `Stok`
- `คลัง 2` → `Stok 2`, `คลัง 3` → `Stok 3`, etc.

New `_normalise_thai_mass_update(df)` function:
1. Checks if any Thai mass_update column names exist in the DataFrame
2. Applies the rename map
3. Applies `คลัง*` → `Stok*` wildcard rename
4. Returns `(df, was_thai)`

**Wiring:** The existing normalisation chain in `_parse_file` (`service.py` lines 64-76) runs `_normalise_thai_columns` for ALL file types when language is not English. This must be gated:

- Gate `_normalise_thai_columns` to only run when `file_type == "order_export"` (it only has order_export mappings anyway, and column name overlap like `"ชื่อสินค้า"` could cause conflicts)
- Add `_normalise_thai_mass_update` for `file_type == "mass_update"`, in the same position

```python
# After English normalisation pass:
if source_language != "en":
    if file_type == "order_export":
        df, was_thai = _normalise_thai_columns(df)
    elif file_type == "mass_update":
        df, was_thai = _normalise_thai_mass_update(df)
    else:
        was_thai = False
    if was_thai:
        source_language = "th"
```

**Column names verified** against actual file `cintage_mass_update_sales_info_205856685_20260325150823.xlsx` (header_row=2, 12,604 rows × 15 cols).

**Files changed:**
- `backend/app/modules/upload/parser.py` — new mapping + function
- `backend/app/modules/upload/service.py` — gate Thai normalisation by file_type
- Tests using the actual Cintage Thai mass update file

## Calculation Impact

None. All three changes are transparent to the calculator layer:
- Memory bump: infrastructure only
- Columnar format: `_extract_parsed_data` reconstructs identical `list[dict]` input
- Thai mapping: columns are renamed to the same Indonesian names the calculators expect

## Test Plan

- [ ] Unit test: `dataframe_to_json` round-trip (rows format → reconstruct dicts == `to_dicts()`)
- [ ] Unit test: `_extract_parsed_data` reads both old `"data"` and new `"rows"` formats
- [ ] Unit test: `_normalise_thai_mass_update` renames all 6 explicit columns + stock wildcard (`คลัง` → `Stok`, `คลัง 2` → `Stok 2`)
- [ ] Unit test: `validate_columns` passes after Thai normalisation on the Cintage file
- [ ] Unit test: incremental ZIP concat produces same result as batch concat
- [ ] Integration: upload the Cintage order export ZIP locally, verify processing succeeds under 1Gi
- [ ] Integration: upload the Cintage Thai mass update locally, verify processing succeeds
