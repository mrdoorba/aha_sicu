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

const ID_DATE = new Intl.DateTimeFormat('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });

export function formatDeadline(date: Date): string {
  return ID_DATE.format(date);
}
