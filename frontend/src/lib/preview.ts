/**
 * The onboarding preview is a UX sandbox: real screens, fake data, no backend.
 *
 * It must never render in production. The check is on the host rather than a
 * build-time flag so that it needs no new GitHub Actions variable and no
 * per-environment config — and so it fails CLOSED: a host we don't recognise
 * gets nothing.
 */
const PREVIEW_HOSTS = new Set([
  'localhost',
  '127.0.0.1',
  '[::1]',
  // Firebase dev target, both domains it serves on.
  'aha-coms-sicu-dev.web.app',
  'aha-coms-sicu-dev.firebaseapp.com',
]);

/**
 * Exact matches only. A prefix test (`/^aha-coms-sicu-dev\./`) would also
 * accept `aha-coms-sicu-dev.attacker.com`, which is a domain anyone can
 * register — the allowlist names whole hosts for that reason.
 */
export function isPreviewEnabled(hostname: string = window.location.hostname): boolean {
  return PREVIEW_HOSTS.has(hostname.toLowerCase());
}
