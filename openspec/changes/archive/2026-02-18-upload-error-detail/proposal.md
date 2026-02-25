## Why

When file uploads fail, users see a generic "Upload failed" message that doesn't convey what the backend actually reported. The signed-url and process mutations already extract `error.detail` from API responses, but the outer error handler in `useUploadFile` doesn't leverage this — losing useful context about what went wrong and at which step.

## What Changes

- Improve the catch block in `useUploadFile` to extract structured error details (e.g., `detail` field) when available
- Provide step-aware context so users know whether failure occurred during signing, uploading, or processing

## Capabilities

### New Capabilities
- `upload-error-reporting`: Upload failures surface the backend's detailed error message instead of a generic fallback

### Modified Capabilities
<!-- None — no existing spec-level requirements are changing -->

## Impact

- `frontend/src/hooks/useUpload.ts`: Modify the catch block in `useUploadFile` (~5-8 lines)
