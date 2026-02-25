## Context

When processing Order Export ZIP files (9 MB, thousands of rows), the Cloud Run container (512 MiB limit) gets OOM-killed during the `/api/v1/upload/process` endpoint. The processing pipeline holds multiple copies of the data simultaneously:

1. `file_bytes` (9 MB raw ZIP)
2. Individual Excel part bytes extracted from ZIP
3. Individual Polars DataFrames per part
4. Concatenated final DataFrame
5. `parsed_data` dict from `dataframe_to_json()` (columns + list of row dicts)

Peak memory holds items 1 + 4 + 5 at once, easily exceeding 512 MiB for large datasets.

Secondary issue: `calculator_service.py` calls `parsed_data.get("columns")` without handling the case where `parsed_data` is a double-encoded JSON string (legacy data). An `_ensure_dict` helper exists in evaluations but isn't used in the calculator's `_validate_columns`.

## Goals / Non-Goals

**Goals:**
- Order Export uploads for files up to ~20 MB / ~10K rows complete without OOM
- Reduce peak memory usage during ZIP processing pipeline
- Fix calculator crash on double-encoded `parsed_data`
- Improve frontend error experience for long-running/failed process requests

**Non-Goals:**
- Streaming/chunked upload from browser (current XHR approach is fine for < 50 MB)
- Changing the `parsed_data` storage schema (JSONB dict format stays)
- Supporting arbitrarily large files (100 MB+) — that would need a fundamentally different architecture

## Decisions

### D1: Increase Cloud Run memory to 1 GiB

**Rationale:** Immediate relief. The current 512 MiB limit is too tight even for moderate workloads (Mass Update at 675 rows already hits 696 MiB). 1 GiB provides comfortable headroom for the optimized code path.

**Alternative considered:** 2 GiB — overkill for current data sizes, increases cost. Can always bump later.

### D2: Eagerly free intermediate data in processing pipeline

**Rationale:** The processing pipeline in `service.py` holds `file_bytes`, the parsed `df`, and the `parsed_data` dict all at once. By explicitly deleting intermediate variables after each stage, we can cut peak memory significantly:

```
Before:  file_bytes + df + parsed_data all in memory (~3x data size)
After:   only one major allocation at a time (~1x data size)
```

Changes:
- `del file_bytes` after ZIP/Excel parsing completes
- `del df` after `dataframe_to_json()` returns
- In `process_zip`: process parts with validation, then concat (already reasonably efficient)

### D3: Use `_ensure_dict` for `parsed_data` in calculator_service

**Rationale:** The `_ensure_dict` helper already exists and is tested. Reuse it in `calculator_service._validate_columns` to handle both dict and double-encoded string cases. This is a defensive fix for legacy data already in the DB.

**Alternative considered:** Data migration to fix double-encoded rows — too risky, `_ensure_dict` is safer and handles the problem at read time.

### D4: Add fetch timeout + better error on frontend process request

**Rationale:** Currently `useUpload.ts` has no timeout on the process step. If the backend takes too long, the browser eventually gets a connection reset that surfaces as a cryptic "NetworkError". Adding an `AbortController` with a reasonable timeout (120s) and a user-friendly error message makes failures actionable.

## Risks / Trade-offs

- **[Memory still tight for very large files]** → 1 GiB + optimizations should handle up to ~20 MB ZIPs comfortably. Larger files would need a different approach (background job + polling). Acceptable risk for now.
- **[`del` statements add code clutter]** → Minimal clutter, significant memory benefit. Python GC doesn't immediately reclaim without explicit `del` when references still exist in the same scope.
- **[Frontend timeout may be too short]** → 120s is generous for processing. If it's still not enough, the real fix is the memory optimization (so processing doesn't OOM and actually completes).
