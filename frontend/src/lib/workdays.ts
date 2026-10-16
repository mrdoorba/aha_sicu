/**
 * Working-day arithmetic for the two 7-day windows: voucher claim and onboarding.
 *
 * Monday–Friday only. Indonesian public holidays are deliberately NOT observed —
 * confirmed with Alfiano on 13 Oct 2026. If that ever changes, it changes here
 * and in the backend's matching helper, nowhere else.
 */

const SATURDAY = 6;
const SUNDAY = 0;

export function isWorkday(date: Date): boolean {
  const day = date.getDay();
  return day !== SATURDAY && day !== SUNDAY;
}

/** The date `count` working days after `from`. `from` itself is never counted. */
export function addWorkdays(from: Date, count: number): Date {
  const out = new Date(from.getTime());
  let remaining = count;
  while (remaining > 0) {
    out.setDate(out.getDate() + 1);
    if (isWorkday(out)) remaining -= 1;
  }
  return out;
}

/**
 * Whole working days from `from` until `to`, floored at 0.
 *
 * Returns 0 for a deadline already reached, so a caller can treat 0 as
 * "expired" without a second comparison.
 */
export function workdaysBetween(from: Date, to: Date): number {
  if (to <= from) return 0;
  const cursor = new Date(from.getTime());
  let days = 0;
  while (cursor < to) {
    cursor.setDate(cursor.getDate() + 1);
    if (cursor <= to && isWorkday(cursor)) days += 1;
  }
  return days;
}

/**
 * When a working day ends, for deadline purposes: 17:00 local time.
 *
 * A deadline printed as a bare date is really a deadline at midnight, which
 * nobody means and nobody staffs. Naming the hour makes the window honest —
 * and it is the hour shown to the brand, so it cannot live only in the backend.
 */
export const BUSINESS_END_HOUR = 17;

/** The same calendar day, at the close of business. */
export function atBusinessEnd(date: Date): Date {
  const out = new Date(date.getTime());
  out.setHours(BUSINESS_END_HOUR, 0, 0, 0);
  return out;
}

/**
 * Whole hours left in today's working day, floored at 0.
 *
 * Zero outside working hours and on a weekend: those hours are not time the
 * brand can use, so counting them would overstate the window.
 */
export function hoursLeftToday(now: Date): number {
  if (!isWorkday(now)) return 0;
  const end = atBusinessEnd(now);
  if (now >= end) return 0;
  return Math.floor((end.getTime() - now.getTime()) / 3_600_000);
}

/**
 * Date formatters, one cached instance per locale.
 *
 * Locale is a parameter rather than a constant because the brand picks the
 * onboarding language and the deadline is the one date they act on — printing
 * '23 Okt' to someone reading the flow in Thai is the kind of small mismatch
 * that makes people doubt the rest of the page. The default keeps every
 * existing caller in the authed app on Indonesian, unchanged.
 */
const DATE_FORMATS = new Map<string, Intl.DateTimeFormat>();
const DATE_TIME_FORMATS = new Map<string, Intl.DateTimeFormat>();

function formatter(
  cache: Map<string, Intl.DateTimeFormat>,
  locale: string,
  options: Intl.DateTimeFormatOptions,
): Intl.DateTimeFormat {
  let found = cache.get(locale);
  if (!found) {
    found = new Intl.DateTimeFormat(locale, options);
    cache.set(locale, found);
  }
  return found;
}

export const DEFAULT_DATE_LOCALE = 'id-ID';

export function formatDeadline(date: Date, locale = DEFAULT_DATE_LOCALE): string {
  return formatter(DATE_FORMATS, locale, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date);
}

/** The deadline with its hour — '23 Okt 2026, 17.00'. */
export function formatDeadlineTime(date: Date, locale = DEFAULT_DATE_LOCALE): string {
  return formatter(DATE_TIME_FORMATS, locale, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}
