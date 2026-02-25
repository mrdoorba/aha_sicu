## Why

File uploads (especially large Order Export .zip files) intermittently show "NetworkError when attempting to fetch resource" even though the backend successfully processes and stores the file. After a page refresh, the upload appears as successful. This creates confusion and unnecessary re-uploads, wasting time and bandwidth.

The root cause: the frontend's process call (`POST /api/v1/upload/process`) can timeout (2-minute `AbortController`) or lose connection before the backend finishes, but the backend continues processing to completion. The frontend shows a false error state.

## What Changes

- Add a **verification step** in the upload error handler: on error, check the backend to see if the upload actually succeeded before displaying the error
- Add a **"verifying" UI state** so users see "Verifying upload…" instead of an immediate false error
- Implement **short polling** (up to 3 retries, 5 seconds apart) to handle cases where backend processing is still in-flight when the error fires
- Capture pre-upload state to compare against, ensuring we don't confuse a previous successful upload with the current one

## Capabilities

### New Capabilities
- `upload-error-recovery`: On upload error, verify with backend whether the upload actually succeeded before showing failure to the user. Includes pre-upload state capture, immediate check, short polling fallback, and "verifying" UI state.

### Modified Capabilities
_(none — `upload-error-reporting` remains unchanged; recovery wraps around it)_

## Impact

- **Frontend only**: `useUpload.ts` (hook logic), `FileUploadSlot.tsx` (UI state)
- No backend changes needed — existing `GET /api/v1/upload/brands/{brand_id}` provides the verification data
- No API changes, no database changes, no new dependencies
