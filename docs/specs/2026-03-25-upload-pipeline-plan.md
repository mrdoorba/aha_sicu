# Upload Pipeline: Memory Fix & Thai Mass Update — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix two production upload failures — OOM on order export processing and missing Thai column mapping for mass_update files.

**Architecture:** Three independent workstreams: (1) bump Cloud Run memory in Terraform tfvars, (2) reduce peak memory in the processing pipeline via incremental ZIP concat and columnar parsed_data storage, (3) add Thai→Indonesian column mapping for mass_update files. All changes are transparent to the calculator layer.

**Tech Stack:** Python 3.14, Polars, FastAPI, Terraform, Cloud Run, PostgreSQL JSONB

**Spec:** `docs/specs/2026-03-25-upload-pipeline-memory-thai-mapping-design.md`

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `infrastructure/terraform/environments/dev.tfvars:15` | Cloud Run memory limit |
| Modify | `infrastructure/terraform/environments/prod.tfvars:15` | Cloud Run memory limit |
| Modify | `backend/app/modules/upload/zip_handler.py:68-89` | Incremental ZIP concat |
| Modify | `backend/app/modules/upload/parser.py:259-273` | Columnar `dataframe_to_json` |
| Modify | `backend/app/modules/upload/parser.py:96-142` | New Thai mass_update mapping + function |
| Modify | `backend/app/modules/upload/service.py:71-75` | Gate Thai normalisation by file_type |
| Modify | `backend/app/modules/evaluations/calculator_service.py:135-161` | Read both parsed_data formats |
| Modify | `backend/tests/unit/test_zip_handler.py` | Test incremental concat |
| Modify | `backend/tests/unit/test_parser.py` | Test Thai mass_update + columnar format |
| Create | `backend/tests/unit/test_calculator_service_extract.py` | Test `_extract_parsed_data` both formats |

---

### Task 1: Bump Cloud Run Memory

**Files:**
- Modify: `infrastructure/terraform/environments/dev.tfvars:15`
- Modify: `infrastructure/terraform/environments/prod.tfvars:15`

- [ ] **Step 1: Update dev.tfvars**

In `infrastructure/terraform/environments/dev.tfvars`, change line 15:
```
cloud_run_memory        = "1Gi"
```

- [ ] **Step 2: Update prod.tfvars**

In `infrastructure/terraform/environments/prod.tfvars`, change line 15:
```
cloud_run_memory        = "1Gi"
```

- [ ] **Step 3: Commit**

```bash
git add infrastructure/terraform/environments/dev.tfvars infrastructure/terraform/environments/prod.tfvars
git commit -m "Bump Cloud Run memory from 512Mi to 1Gi

The door cannot open when the room has no air. A 3.2 MB order export
ZIP (11K rows × 59 cols) exceeded the 512 MiB limit during Excel
parsing. Doubling to 1 GiB provides headroom while pipeline
optimisations land in subsequent commits.

Author: Mr. Door"
```

---

### Task 2: Incremental ZIP Concat

**Files:**
- Modify: `backend/app/modules/upload/zip_handler.py:68-89`
- Modify: `backend/tests/unit/test_zip_handler.py`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/unit/test_zip_handler.py`:

```python
def test_process_zip_incremental_concat_matches_batch():
    """Incremental concat produces identical result to batch concat."""
    df1 = pl.DataFrame({"Col_A": [1, 2], "Col_B": ["a", "b"]})
    df2 = pl.DataFrame({"Col_A": [3, 4], "Col_B": ["c", "d"]})
    df3 = pl.DataFrame({"Col_A": [5, 6], "Col_B": ["e", "f"]})
    zip_bytes = _make_zip({
        "data_part_1_of_3.xlsx": df1,
        "data_part_2_of_3.xlsx": df2,
        "data_part_3_of_3.xlsx": df3,
    })
    result = process_zip(zip_bytes, "order_export")
    assert len(result) == 6
    assert result["Col_A"].to_list() == [1, 2, 3, 4, 5, 6]
    assert result["Col_B"].to_list() == ["a", "b", "c", "d", "e", "f"]
```

- [ ] **Step 2: Run test to verify it passes (baseline)**

```bash
cd backend && uv run pytest tests/unit/test_zip_handler.py::test_process_zip_incremental_concat_matches_batch -v
```
Expected: PASS (existing batch concat also produces this result — this test locks the behavior before we change the implementation).

- [ ] **Step 3: Implement incremental concat**

In `backend/app/modules/upload/zip_handler.py`, replace lines 68-89:

```python
        header_row = 2 if file_type == "mass_update" else 0
        result_df: pl.DataFrame | None = None
        reference_columns: list[str] | None = None

        for entry_name in excel_entries:
            entry_bytes = zf.read(entry_name)
            df = parse_excel(entry_bytes, header_row=header_row)

            if reference_columns is None:
                reference_columns = df.columns
            elif df.columns != reference_columns:
                raise UploadException(
                    code="UPLOAD_ZIP_STRUCTURE_MISMATCH",
                    detail=(
                        f"Excel parts have different column structures. "
                        f"Expected columns from first part: {reference_columns}, "
                        f"but '{entry_name}' has: {df.columns}"
                    ),
                )

            result_df = df if result_df is None else pl.concat([result_df, df])

        return result_df
```

- [ ] **Step 4: Run all zip_handler tests**

```bash
cd backend && uv run pytest tests/unit/test_zip_handler.py -v
```
Expected: All PASS (including the new test and all existing tests).

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/upload/zip_handler.py backend/tests/unit/test_zip_handler.py
git commit -m "Use incremental concat for ZIP part merging

Each part now merges with the running result as it arrives, so only
two DataFrames coexist at once. The previous approach held all N parts
simultaneously — for a 10-part ZIP that meant 10× peak memory.

Author: Mr. Door"
```

---

### Task 3: Columnar parsed_data Storage Format

**Files:**
- Modify: `backend/app/modules/upload/parser.py:259-273`
- Modify: `backend/tests/unit/test_parser.py`

- [ ] **Step 1: Remove old tests and write new tests for columnar format**

In `backend/tests/unit/test_parser.py`, **remove** the existing `test_dataframe_to_json` and `test_dataframe_to_json_english` functions (lines 143-156) — they assert the old `"data"` key format and will break. Replace with the new `TestDataframeToJson` class:

```python
from app.modules.upload.parser import dataframe_to_json


class TestDataframeToJson:
    """Tests for dataframe_to_json columnar format."""

    def test_produces_rows_format(self):
        df = pl.DataFrame({"A": [1, 2], "B": ["x", "y"]})
        result = dataframe_to_json(df)
        assert "rows" in result
        assert "data" not in result
        assert result["columns"] == ["A", "B"]
        assert result["rows"] == [list(r) for r in df.rows()]
        assert result["row_count"] == 2

    def test_round_trip_equivalence(self):
        """Reconstructed dicts from rows format == to_dicts() output."""
        df = pl.DataFrame({
            "Name": ["Alice", "Bob"],
            "Age": [30, 25],
            "Score": [9.5, 8.0],
        })
        result = dataframe_to_json(df)
        columns = result["columns"]
        reconstructed = [dict(zip(columns, row)) for row in result["rows"]]
        assert reconstructed == df.to_dicts()

    def test_preserves_source_language(self):
        df = pl.DataFrame({"A": [1]})
        result = dataframe_to_json(df, source_language="th")
        assert result["source_language"] == "th"

    def test_empty_dataframe(self):
        df = pl.DataFrame({"A": pl.Series([], dtype=pl.Int64)})
        result = dataframe_to_json(df)
        assert result["rows"] == []
        assert result["row_count"] == 0
        assert result["columns"] == ["A"]

    def test_wide_dataframe_no_repeated_keys(self):
        """59-column DataFrame should not repeat column names in rows."""
        cols = {f"Col_{i}": [i] for i in range(59)}
        df = pl.DataFrame(cols)
        result = dataframe_to_json(df)
        # Each row is a tuple of 59 values, not a dict of 59 keys
        assert len(result["rows"][0]) == 59
        assert not isinstance(result["rows"][0], dict)
```

**Note:** `df.rows()` returns tuples, not lists. Tests compare against `df.rows()` output or use structural checks rather than literal list comparisons. After JSONB round-trip (write tuple → JSON array → read list), `_extract_parsed_data` handles both.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/unit/test_parser.py::TestDataframeToJson -v
```
Expected: FAIL — `"rows"` key not in result, `"data"` key exists instead.

- [ ] **Step 3: Implement columnar format**

In `backend/app/modules/upload/parser.py`, replace `dataframe_to_json` (lines 259-273):

```python
def dataframe_to_json(
    df: pl.DataFrame, *, source_language: str = "id"
) -> dict[str, Any]:
    """Convert a Polars DataFrame to a JSON-serializable dict for JSONB storage.

    Uses columnar rows format (list-of-lists) instead of list-of-dicts
    to avoid repeating column names for every row.

    Args:
        df: The DataFrame to convert.
        source_language: ``"en"``, ``"id"``, or ``"th"`` — detected language.
    """
    return {
        "columns": df.columns,
        "rows": df.rows(),
        "row_count": len(df),
        "source_language": source_language,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/unit/test_parser.py::TestDataframeToJson -v
```
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/upload/parser.py backend/tests/unit/test_parser.py
git commit -m "Switch parsed_data to columnar rows format

The old list-of-dicts format repeated every column name in every row —
for a 59-column file, that meant 649K redundant strings. The new format
stores rows as lists of values alongside a single columns array.

Author: Mr. Door"
```

---

### Task 4: Update _extract_parsed_data for Both Formats

**Files:**
- Modify: `backend/app/modules/evaluations/calculator_service.py:135-161`
- Create: `backend/tests/unit/test_calculator_service_extract.py`

- [ ] **Step 1: Write tests for both formats**

Create `backend/tests/unit/test_calculator_service_extract.py`:

```python
"""Tests for _extract_parsed_data backward compatibility."""

import pytest

from app.core.exceptions import CalculatorException
from app.modules.evaluations.calculator_service import _extract_parsed_data


class TestExtractParsedData:
    """_extract_parsed_data reads both old and new formats."""

    def test_reads_new_rows_format(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "rows": [[1, "x"], [2, "y"]],
                "row_count": 2,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}]

    def test_reads_old_data_format(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "data": [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}],
                "row_count": 2,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1, "B": "x"}, {"A": 2, "B": "y"}]

    def test_prefers_rows_over_data(self):
        """If both keys exist (shouldn't happen), prefer rows."""
        upload = {
            "parsed_data": {
                "columns": ["A"],
                "rows": [[1]],
                "data": [{"A": 999}],
                "row_count": 1,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1}]

    def test_empty_rows(self):
        upload = {
            "parsed_data": {
                "columns": ["A", "B"],
                "rows": [],
                "row_count": 0,
            }
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == []

    def test_invalid_parsed_data_raises(self):
        upload = {"parsed_data": None}
        with pytest.raises(CalculatorException) as exc:
            _extract_parsed_data(upload, "order_export")
        assert exc.value.code == "CALC_MISSING_DATA"

    def test_missing_both_keys_raises(self):
        upload = {
            "parsed_data": {
                "columns": ["A"],
                "row_count": 0,
            }
        }
        with pytest.raises(CalculatorException) as exc:
            _extract_parsed_data(upload, "order_export")
        assert exc.value.code == "CALC_MISSING_DATA"

    def test_json_string_with_rows_format(self):
        """Handle double-encoded JSON string (rows format)."""
        import json
        upload = {
            "parsed_data": json.dumps({
                "columns": ["A"],
                "rows": [[1], [2]],
                "row_count": 2,
            })
        }
        result = _extract_parsed_data(upload, "order_export")
        assert result == [{"A": 1}, {"A": 2}]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/unit/test_calculator_service_extract.py -v
```
Expected: `test_reads_new_rows_format` FAILS (current code looks for `"data"` key only).

- [ ] **Step 3: Implement backward-compatible reader**

In `backend/app/modules/evaluations/calculator_service.py`, replace `_extract_parsed_data` (lines 135-161):

```python
def _extract_parsed_data(upload: dict, file_type: str) -> list[dict[str, Any]]:
    """Extract and validate parsed_data from a brand upload record.

    Supports both formats:
    - New: ``{"columns": [...], "rows": [[v1, v2], ...]}``
    - Old: ``{"columns": [...], "data": [{"col": v1}, ...]}``

    Raises:
        CalculatorException: CALC_MISSING_DATA if parsed_data structure is invalid.
    """
    parsed_data = upload.get("parsed_data")
    if isinstance(parsed_data, str):
        import json
        try:
            parsed_data = json.loads(parsed_data)
        except (json.JSONDecodeError, TypeError):
            parsed_data = None
    if not isinstance(parsed_data, dict):
        raise CalculatorException(
            code="CALC_MISSING_DATA",
            detail=f"Upload '{file_type}' has invalid parsed_data structure",
        )

    # New columnar format: reconstruct list[dict] from columns + rows
    rows = parsed_data.get("rows")
    if isinstance(rows, list):
        columns = parsed_data.get("columns", [])
        return [dict(zip(columns, row)) for row in rows]

    # Old row-dict format: return as-is
    data = parsed_data.get("data")
    if isinstance(data, list):
        return data

    raise CalculatorException(
        code="CALC_MISSING_DATA",
        detail=f"Upload '{file_type}' has invalid parsed_data.data structure",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/unit/test_calculator_service_extract.py -v
```
Expected: All PASS.

- [ ] **Step 5: Run full test suite to check no regressions**

```bash
cd backend && uv run pytest tests/ -v --timeout=30
```
Expected: All existing tests PASS. The calculators that relied on `"data"` key now go through the old-format fallback path.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/evaluations/calculator_service.py backend/tests/unit/test_calculator_service_extract.py
git commit -m "Support both columnar and row-dict parsed_data formats

A door that opens only one way is a wall. The reader now checks for
the new 'rows' key first (list-of-lists), then falls back to the old
'data' key (list-of-dicts). All five call sites across three
calculators receive identical list[dict] output.

Author: Mr. Door"
```

---

### Task 5: Thai Mass Update Column Mapping

**Files:**
- Modify: `backend/app/modules/upload/parser.py:96-142`
- Modify: `backend/tests/unit/test_parser.py`

- [ ] **Step 1: Write the failing tests**

Add to `backend/tests/unit/test_parser.py`:

```python
from app.modules.upload.parser import _normalise_thai_mass_update


def _thai_mass_update_df(**overrides: list) -> pl.DataFrame:
    """Build a DataFrame with Thai mass update headers."""
    base = {
        "รหัสสินค้า": ["P1", "P2"],
        "ชื่อสินค้า": ["Product A", "Product B"],
        "รหัสตัวเลือกสินค้า": ["V1", "V2"],
        "ชื่อตัวเลือกสินค้า": ["Red", "Blue"],
        "เลข SKU": ["SKU1", "SKU2"],
        "ราคา": [100, 200],
        "คลัง": [50, 30],
    }
    base.update(overrides)
    return pl.DataFrame(base)


class TestThaiMassUpdateNormalisation:
    """Tests for _normalise_thai_mass_update."""

    def test_renames_all_columns_to_indonesian(self):
        df = _thai_mass_update_df()
        result, was_thai = _normalise_thai_mass_update(df)

        assert was_thai is True
        assert "Kode Produk" in result.columns
        assert "Nama Produk" in result.columns
        assert "Kode Variasi" in result.columns
        assert "Nama Variasi" in result.columns
        assert "SKU" in result.columns
        assert "Harga" in result.columns
        assert "Stok" in result.columns

    def test_validates_after_normalisation(self):
        """Thai mass update passes column validation after normalisation."""
        df = _thai_mass_update_df()
        result, _ = _normalise_thai_mass_update(df)
        validate_columns(result, "mass_update")  # should not raise

    def test_stock_wildcard_multi_warehouse(self):
        """คลัง, คลัง 2, คลัง 3 → Stok, Stok 2, Stok 3."""
        df = _thai_mass_update_df(**{
            "คลัง 2": [10, 20],
            "คลัง 3": [5, 15],
        })
        result, was_thai = _normalise_thai_mass_update(df)
        assert was_thai is True
        assert "Stok" in result.columns
        assert "Stok 2" in result.columns
        assert "Stok 3" in result.columns
        assert "คลัง" not in result.columns
        assert "คลัง 2" not in result.columns
        assert "คลัง 3" not in result.columns

    def test_indonesian_passthrough(self):
        """Indonesian DataFrames pass through unchanged."""
        cols = REQUIRED_COLUMNS["mass_update"]
        df = pl.DataFrame({col: ["x"] for col in cols})
        result, was_thai = _normalise_thai_mass_update(df)
        assert was_thai is False
        assert result.columns == df.columns

    def test_preserves_extra_columns(self):
        """Non-mapped columns are kept as-is."""
        df = _thai_mass_update_df(**{"GTIN": ["123"]})
        result, _ = _normalise_thai_mass_update(df)
        assert "GTIN" in result.columns
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend && uv run pytest tests/unit/test_parser.py::TestThaiMassUpdateNormalisation -v
```
Expected: FAIL — `_normalise_thai_mass_update` does not exist.

- [ ] **Step 3: Implement the mapping and function**

In `backend/app/modules/upload/parser.py`, add after `_normalise_thai_columns` (after line 142):

```python
# ---------------------------------------------------------------------------
# Thai → Indonesian normalisation for Shopee Thailand mass update exports
# ---------------------------------------------------------------------------

_MASS_UPDATE_COLUMN_RENAME_TH: dict[str, str] = {
    "รหัสสินค้า": "Kode Produk",
    "ชื่อสินค้า": "Nama Produk",
    "รหัสตัวเลือกสินค้า": "Kode Variasi",
    "ชื่อตัวเลือกสินค้า": "Nama Variasi",
    "เลข SKU": "SKU",
    "ราคา": "Harga",
}


def _normalise_thai_mass_update(df: pl.DataFrame) -> tuple[pl.DataFrame, bool]:
    """Rename Thai Shopee mass-update columns to Indonesian.

    Also renames ``คลัง*`` columns to ``Stok*`` so the calculator's
    ``startswith("Stok")`` lookup works for multi-warehouse files.

    Returns:
        Tuple of (normalised DataFrame, was_thai) where was_thai is True
        if Thai column renames were applied.
    """
    actual = set(df.columns)
    rename_map = {th: id_ for th, id_ in _MASS_UPDATE_COLUMN_RENAME_TH.items() if th in actual}

    # Rename "คลัง", "คลัง 2", "คลัง 3", … → "Stok", "Stok 2", "Stok 3", …
    for col in actual:
        if col == "คลัง":
            rename_map[col] = "Stok"
        elif col.startswith("คลัง "):
            rename_map[col] = "Stok " + col[len("คลัง "):]

    if not rename_map:
        return df, False

    df = df.rename(rename_map)
    return df, True
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend && uv run pytest tests/unit/test_parser.py::TestThaiMassUpdateNormalisation -v
```
Expected: All PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/upload/parser.py backend/tests/unit/test_parser.py
git commit -m "Add Thai column mapping for mass_update file uploads

A new threshold is crossed — Thai sellers may now upload mass update
exports in their native tongue. Maps รหัสสินค้า → Kode Produk,
ชื่อสินค้า → Nama Produk, and five others including the คลัง* → Stok*
wildcard for multi-warehouse stock columns.

Author: Mr. Door"
```

---

### Task 6: Wire Thai Mass Update Normalisation into _parse_file

**Files:**
- Modify: `backend/app/modules/upload/service.py:64-75`

- [ ] **Step 1: Update the normalisation chain**

In `backend/app/modules/upload/service.py`, replace lines 64-75:

```python
    # Normalise English columns → Indonesian (CSV already does this in
    # parse_csv, but Excel/ZIP files need it here)
    if source_language == "id":  # skip if parse_csv already detected English
        df, was_english = _normalise_english_columns(df)
        if was_english:
            source_language = "en"

    # Normalise Thai columns → Indonesian (gated by file_type)
    if source_language != "en":  # Thai and English are mutually exclusive
        if file_type == "order_export":
            df, was_thai = _normalise_thai_columns(df)
        elif file_type == "mass_update":
            df, was_thai = _normalise_thai_mass_update(df)
        else:
            was_thai = False
        if was_thai:
            source_language = "th"
```

- [ ] **Step 2: Add import**

In `backend/app/modules/upload/service.py`, update the import from parser (around line 19-26) to include `_normalise_thai_mass_update`:

```python
from app.modules.upload.parser import (
    _normalise_english_columns,
    _normalise_thai_columns,
    _normalise_thai_mass_update,
    dataframe_to_json,
    parse_csv,
    parse_excel,
    validate_columns,
)
```

- [ ] **Step 3: Write test for file_type gating**

Add to `backend/tests/unit/test_parser.py`:

```python
from tests.unit.conftest import make_excel_bytes


class TestParseFileThaiGating:
    """Verify _parse_file gates Thai normalisation by file_type."""

    def test_thai_mass_update_gets_mass_update_mapping(self):
        """Thai mass_update file should use _normalise_thai_mass_update, not _normalise_thai_columns."""
        from app.modules.upload.service import _parse_file

        df = _thai_mass_update_df()
        file_bytes = make_excel_bytes(df, header_row=2)
        result_df, lang = _parse_file(file_bytes, "test.xlsx", "mass_update")

        assert lang == "th"
        assert "Kode Produk" in result_df.columns
        assert "Nama Produk" in result_df.columns
        # Should NOT have order_export columns like "No. Pesanan"
        assert "No. Pesanan" not in result_df.columns

    def test_thai_order_export_gets_order_export_mapping(self):
        """Thai order_export file should still use _normalise_thai_columns."""
        from app.modules.upload.service import _parse_file

        df = _thai_order_df()
        file_bytes = make_excel_bytes(df)
        result_df, lang = _parse_file(file_bytes, "test.xlsx", "order_export")

        assert lang == "th"
        assert "No. Pesanan" in result_df.columns
        # Should NOT have mass_update columns like "Kode Variasi"
        assert "Kode Variasi" not in result_df.columns
```

- [ ] **Step 4: Run full test suite**

```bash
cd backend && uv run pytest tests/ -v --timeout=30
```
Expected: All PASS. Existing Thai order_export tests still pass (gated to `file_type == "order_export"`). Thai mass_update normalisation is now wired in. Gating tests verify no cross-contamination.

- [ ] **Step 5: Verify with actual Cintage file**

```bash
cd backend && uv run python -c "
from app.modules.upload.service import _parse_file
import pathlib

file_bytes = pathlib.Path('/Users/mac/HT/Project/aha_sicu/my-local-resources/Files Upload/Cintage/cintage_mass_update_sales_info_205856685_20260325150823.xlsx').read_bytes()
df, lang = _parse_file(file_bytes, 'cintage_mass_update_sales_info_205856685_20260325150823.xlsx', 'mass_update')
print(f'Language: {lang}')
print(f'Columns: {df.columns}')
print(f'Rows: {len(df)}')
print(f'Has Stok: {any(c.startswith(\"Stok\") for c in df.columns)}')
from app.modules.upload.parser import validate_columns
validate_columns(df, 'mass_update')
print('Column validation: PASSED')
"
```
Expected: Language=th, all Indonesian column names present, Stok column exists, validation passes.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/upload/service.py backend/tests/unit/test_parser.py
git commit -m "Gate Thai normalisation by file_type in _parse_file

Each file type now receives only its own Thai mapping — order_export
gets _normalise_thai_columns, mass_update gets _normalise_thai_mass_update.
The previous code ran order_export mappings on all file types, which
could cause subtle conflicts when column names overlap.

Author: Mr. Door"
```

---

### Task 7: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
cd backend && uv run pytest tests/ -v --timeout=30
```
Expected: All PASS.

- [ ] **Step 2: Verify order export ZIP round-trip**

```bash
cd backend && uv run python -c "
from app.modules.upload.service import _parse_file
from app.modules.upload.parser import dataframe_to_json
import pathlib

file_bytes = pathlib.Path('/Users/mac/HT/Project/aha_sicu/my-local-resources/Files Upload/Cintage/cintage_Order.all.20260201_20260228.zip').read_bytes()
df, lang = _parse_file(file_bytes, 'order.all.20260201_20260228.zip', 'order_export')
print(f'Language: {lang}, Rows: {len(df)}, Cols: {len(df.columns)}')

# Verify columnar format round-trip
result = dataframe_to_json(df, source_language=lang)
columns = result['columns']
reconstructed = [dict(zip(columns, row)) for row in result['rows']]
original = df.to_dicts()
assert reconstructed == original, 'Round-trip mismatch!'
print(f'Round-trip: PASSED ({len(reconstructed)} rows)')
"
```
Expected: Round-trip passes for the actual production file.

- [ ] **Step 3: Verify clean working tree**

```bash
git status
```
Expected: Clean working tree. All changes committed across Tasks 1-6.
