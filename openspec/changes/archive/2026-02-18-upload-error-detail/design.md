## Context

`useUploadFile` has a 3-step pipeline (sign → upload → process). Steps 1 and 3 use mutations that already extract `error.detail` from API responses and throw `new Error(detail)`. The outer catch block at line 151 reads `err.message`, which works for those cases. However, if the error object carries a `detail` property directly (e.g., from the API client), it's not extracted.

The existing pattern in `useRequestSignedUrl` and `useProcessUpload` (lines 47-48, 78-79) casts the error and reads `.detail`. We'll apply the same pattern in the outer catch.

## Goals / Non-Goals

**Goals:**
- Surface backend error details to the user when available
- Maintain consistency with the error extraction pattern already used in this file

**Non-Goals:**
- Changing the error handling in `useRequestSignedUrl` or `useProcessUpload` (already correct)
- Adding error classification or retry logic
- Modifying backend error response formats

## Decisions

### Extract `detail` from error objects in the catch block

Use the same `(error as Record<string, unknown>).detail` pattern from lines 47 and 78. This keeps the approach consistent within the file.

**Alternative considered:** Creating a shared `extractErrorMessage` helper. Rejected — only one call site benefits, and the pattern is already a 1-liner.

## Risks / Trade-offs

- [Minimal risk] The `detail` field could theoretically contain a non-user-friendly message → Acceptable, since the same approach is already used in the two mutation hooks without issues.
