## 1. Infrastructure — Cloud Run Memory

- [x] 1.1 Increase Cloud Run dev service memory from 512Mi to 1Gi (deploy config or gcloud command)

## 2. Backend — Memory Optimization

- [x] 2.1 Add `del file_bytes` in `service.py` after ZIP/Excel parsing completes
- [x] 2.2 Add `del df` in `service.py` after `dataframe_to_json()` returns

## 3. Backend — Fix Double-Encoded parsed_data in Calculators

- [x] 3.1 Move `_ensure_dict` from `evaluations/service.py` to a shared utility (or import it in calculator_service)
- [x] 3.2 Apply `_ensure_dict` to `parsed_data` in `calculator_service._validate_columns` before calling `.get("columns")`
- [x] 3.3 Add test for `_validate_columns` with string `parsed_data` input

## 4. Frontend — Process Timeout & Error Messaging

- [x] 4.1 Add `AbortController` with 120s timeout to the process step in `useUpload.ts`
- [x] 4.2 Detect abort/timeout error and display user-friendly message ("Processing timed out. The file may be too large — try splitting it into smaller parts.")

## 5. Verification

- [x] 5.1 Run backend tests (`uv run pytest -v`)
- [x] 5.2 Run frontend lint + typecheck (`npm run lint && npx tsc --noEmit`)
