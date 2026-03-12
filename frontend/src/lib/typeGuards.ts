// ── Runtime type guards ─────────────────────────────────────────────────────
// Every `unknown` boundary deserves a runtime check, not a cast.
// These guards narrow to the EXACT expected type.

/**
 * Narrows an unknown error to an object with a `detail` string property.
 * Used across API error handlers where the backend returns `{ detail: string }`.
 */
export function isApiErrorWithDetail(
  err: unknown,
): err is { detail: string } {
  return (
    typeof err === 'object' &&
    err !== null &&
    'detail' in err &&
    typeof (err as Record<string, unknown>).detail === 'string'
  );
}

/**
 * Narrows an unknown error to an object with `detail` and optional `code` string properties.
 * Used where we need to distinguish specific error codes (e.g. EVAL_NOT_FOUND).
 */
export function isApiErrorWithCode(
  err: unknown,
): err is { detail: string; code?: string } {
  return (
    isApiErrorWithDetail(err) &&
    (!('code' in err) || typeof (err as Record<string, unknown>).code === 'string')
  );
}

/**
 * Narrows unknown to a Record<string, unknown> — the safest way to
 * access properties on an untyped object boundary.
 */
export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Narrows unknown to an Array of Record<string, unknown>.
 */
export function isRecordArray(value: unknown): value is Array<Record<string, unknown>> {
  return Array.isArray(value) && value.every(isRecord);
}

/**
 * Convert a typed object to Record<string, unknown> via spreading.
 * The righteous alternative to `as unknown as Record<string, unknown>`.
 */
export function toRecord(value: object): Record<string, unknown> {
  return { ...value };
}

/**
 * Safely extract an error message from an unknown catch target.
 * Prefers `.detail` (API errors), falls back to `.message` (Error instances),
 * then a generic fallback string.
 */
export function extractErrorMessage(err: unknown, fallback: string): string {
  if (isApiErrorWithDetail(err)) return err.detail;
  if (err instanceof Error) return err.message;
  return fallback;
}
