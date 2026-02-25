## Context

The upload flow uses a 3-stage architecture: (1) get signed URL from backend, (2) upload file directly to GCS via XHR, (3) trigger backend processing via `POST /api/v1/upload/process`. The process call has a 2-minute `AbortController` timeout on the frontend.

For large files (Order Export .zip with ~40K rows), the backend processing can exceed 2 minutes — parsing, validating, storing to DB, running auto-calculators. When the frontend aborts, the backend continues processing to completion. The frontend shows an error, but the data is actually saved.

Current flow in `useUpload.ts`: any error in the try/catch → immediately sets `status: 'error'` with an error message. No verification step exists.

## Goals / Non-Goals

**Goals:**
- Eliminate false-negative upload errors by verifying with the backend before displaying failure
- Keep users informed during verification with a clear "verifying" UI state
- Handle the in-flight processing case where backend hasn't finished yet at error time

**Non-Goals:**
- Increasing the process timeout (would just shift the threshold, not fix the race)
- Adding retry logic for the actual upload/process calls (different problem)
- Backend changes (existing `GET /brands/{brand_id}` endpoint suffices)
- Handling genuine upload failures differently (those still show as errors after verification)

## Decisions

### Decision 1: Pre-upload state capture for comparison

**Choice:** Before starting an upload, snapshot the current upload record (filename + uploaded_at) for the target file_type from the React Query cache.

**Why:** After an error, we need to distinguish "the backend saved our new upload" from "we're seeing a previous upload that was already there." Comparing the filename and/or timestamp against the pre-upload snapshot handles this reliably.

**Alternative considered:** Add a backend endpoint to check upload status by `upload_id`. Rejected — adds unnecessary backend complexity when the existing list endpoint + comparison achieves the same result.

### Decision 2: Hybrid verify + short poll

**Choice:** On error, enter a "verifying" state:
1. Immediately invalidate and refetch `brandUploads` query
2. Compare the returned upload for this file_type against pre-upload snapshot
3. If changed → upload succeeded, transition to `done`
4. If unchanged → wait 5 seconds, retry (up to 3 times = 15 seconds max)
5. If still unchanged after all retries → transition to `error` with original message

**Why:** The immediate check handles cases where the backend already finished. The short poll handles the in-flight case (backend is still processing when the frontend error fires). 15 seconds max avoids indefinite waiting.

**Alternative considered:** Pure immediate check (no polling). Rejected — would miss the common case where the process call times out while backend is mid-processing.

### Decision 3: New "verifying" upload status

**Choice:** Add `'verifying'` to the `UploadStatus` union type. Display as a spinner with "Verifying upload…" text in `FileUploadSlot`.

**Why:** Users need to know something is happening after the error. Showing the error first then flipping to success is jarring. Showing "verifying" is honest and reassuring.

### Decision 4: Verification logic lives in the `useUploadFile` hook

**Choice:** All verification logic stays inside the existing `catch` block of `useUploadFile.upload()`, keeping the component layer unchanged except for the new status string.

**Why:** The hook already manages all upload state transitions. Adding verification here keeps the logic centralized and avoids prop-drilling or new hooks.

## Risks / Trade-offs

- **[15-second delay on genuine errors]** → Acceptable trade-off. Genuine errors are rare; false errors on large files are frequent. Users see "Verifying…" so they know the system is working.
- **[Race condition: refetch returns stale cache]** → Mitigated by `invalidateQueries` before refetch, forcing a fresh network request.
- **[Upload succeeded but auto-calculators failed]** → The upload record will still be in DB (backend wraps auto-calc in try/except). Verification will correctly detect success. Calculator status refreshes on next page load.
