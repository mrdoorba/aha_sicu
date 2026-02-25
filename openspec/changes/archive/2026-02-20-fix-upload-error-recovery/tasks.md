## 1. Upload Hook — Verification Logic

- [x] 1.1 Add `'verifying'` to the `UploadStatus` type union in `useUpload.ts`
- [x] 1.2 Add pre-upload state capture: before the first network call in `upload()`, snapshot the current upload record (filename, uploaded_at) for the target file_type from the React Query cache
- [x] 1.3 Implement verification function: on error, invalidate + refetch `brandUploads`, compare the upload record for the file_type against the snapshot; return whether the upload changed
- [x] 1.4 Implement short poll loop: if immediate check shows no change, retry up to 3 times at 5-second intervals, with cancellation support (abort on new upload or component unmount)
- [x] 1.5 Wire verification into the `catch` block: set status to `'verifying'`, run verify, then transition to `'done'` (if confirmed) or `'error'` (if genuinely failed). On confirmed success, invalidate calculatorResults and calculatorStatus queries.

## 2. UI — Verifying State

- [x] 2.1 Update `FileUploadSlot.tsx` to handle `'verifying'` status: display spinner with "Verifying upload…" text (same visual style as uploading/processing states)

## 3. Testing

- [x] 3.1 Add unit tests for the verification logic: mock scenarios for immediate success, poll-then-success, and genuine failure
- [x] 3.2 Verify TypeScript compiles cleanly (`npx tsc --noEmit`)
- [x] 3.3 Run frontend linting and existing tests to ensure no regressions
