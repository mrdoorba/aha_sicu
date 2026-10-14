import {
  addWorkdays,
  formatDeadline,
  workdaysBetween,
} from '../../lib/workdays';

export { formatDeadline };

/**
 * Read a `?sisa=N` override off the URL.
 *
 * A fresh preview always sits on day 7 with a full bar, which is exactly the
 * frame that shows nothing. `?sisa=2` lets a reviewer see the bar part-spent
 * and the colour escalate without waiting five days for it.
 */
export function remainingFromSearch(search: string): number | null {
  const raw = new URLSearchParams(search).get('sisa')?.trim();
  // `?sisa=` parses as 0 through Number(''), which would silently render an
  // expired voucher from what is really a missing value.
  if (!raw) return null;
  const n = Number(raw);
  return Number.isInteger(n) ? n : null;
}

/**
 * The preview's onboarding deadline: 7 working days from now, recomputed on
 * every render so the countdown is real rather than a frozen screenshot.
 */
export function previewDeadlineLabel(search = ''): {
  date: Date;
  workdays: number;
} {
  const now = new Date();
  const override = remainingFromSearch(search);
  const date = addWorkdays(now, override ?? 7);
  return { date, workdays: override ?? workdaysBetween(now, date) };
}

/** A claimed voucher gives the brand 7 working days to finish onboarding. */
export const TOTAL_WORKDAYS = 7;

export type DeadlineUrgency = 'calm' | 'soon' | 'critical';

/**
 * How full the bar is, and how loudly it says so.
 *
 * Separate from the component because it is the part worth testing: the bar
 * SHRINKS as the deadline approaches, so `remaining` drives width directly and
 * an off-by-one here would be invisible in a screenshot but wrong on day 7.
 */
export function deadlineMeter(
  remaining: number,
  total: number = TOTAL_WORKDAYS,
) {
  const clamped = Math.max(0, Math.min(remaining, total));
  const urgency: DeadlineUrgency =
    clamped <= 1 ? 'critical' : clamped <= 3 ? 'soon' : 'calm';
  // A bar at literally 0% reads as 'broken', not as 'out of time', so an
  // expired voucher keeps a sliver that the colour explains.
  const percent = clamped === 0 ? 3 : (clamped / total) * 100;
  return { clamped, urgency, percent, expired: clamped === 0 };
}
