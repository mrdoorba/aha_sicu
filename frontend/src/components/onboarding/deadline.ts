import {
  addWorkdays,
  atBusinessEnd,
  formatDeadline,
  formatDeadlineTime,
  hoursLeftToday,
  workdaysBetween,
} from '../../lib/workdays';

export { formatDeadline, formatDeadlineTime };

/**
 * Read a `?sisa=N` override off the URL.
 *
 * A fresh preview always sits on day 7 with a full bar, which is exactly the
 * frame that shows nothing. `?sisa=2` lets a reviewer see the bar part-spent
 * and the colour escalate without waiting five days for it.
 */
export function remainingFromSearch(search: string, key = 'sisa'): number | null {
  const raw = new URLSearchParams(search).get(key)?.trim();
  // `?sisa=` parses as 0 through Number(''), which would silently render an
  // expired voucher from what is really a missing value.
  if (!raw) return null;
  const n = Number(raw);
  return Number.isInteger(n) ? n : null;
}

/**
 * The preview's onboarding deadline: 7 working days from now, at the close of
 * business, recomputed on every render so the countdown is real rather than a
 * frozen screenshot.
 *
 * `?jam=N` overrides the hours alongside `?sisa=N`, because the last few hours
 * are the frame worth checking and nobody is going to sit at the preview until
 * 16:00 to see it.
 */
export function previewDeadlineLabel(search = ''): {
  date: Date;
  workdays: number;
  hours: number;
} {
  const now = new Date();
  const days = remainingFromSearch(search);
  const hours = remainingFromSearch(search, 'jam');
  const date = atBusinessEnd(addWorkdays(now, days ?? 7));
  return {
    date,
    workdays: days ?? workdaysBetween(now, date),
    hours: hours ?? hoursLeftToday(now),
  };
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
  hoursLeft = 0,
) {
  const clamped = Math.max(0, Math.min(remaining, total));
  const hours = Math.max(0, hoursLeft);
  const urgency: DeadlineUrgency =
    clamped <= 1 ? 'critical' : clamped <= 3 ? 'soon' : 'calm';
  // A bar at literally 0% reads as 'broken', not as 'out of time', so an
  // expiring window keeps a sliver that the colour explains.
  const percent = clamped === 0 ? 3 : (clamped / total) * 100;
  // Hours matter most on the last day: 0 working days but 4 hours left is a
  // brand that can still finish, and calling that expired would be wrong.
  return { clamped, hours, urgency, percent, expired: clamped === 0 && hours === 0 };
}

/**
 * The remaining-time sentence, as a translation key plus its numbers.
 *
 * A key rather than a finished string because this file is pure and the flow
 * is now ID/EN/TH: handing `t` into the arithmetic would make the one piece
 * worth unit-testing depend on an i18n instance. Hours are carried alongside
 * the days rather than only at the end, because 'sisa 1 hari kerja' is read as
 * a full day by someone looking at it at 16:30.
 */
export function remainingLabel(
  days: number,
  hours: number,
): { key: string; vars: { days: number; hours: number } } {
  const vars = { days, hours };
  if (days === 0 && hours === 0) return { key: 'onboarding.deadline.expired', vars };
  if (days === 0) return { key: 'onboarding.deadline.hours', vars };
  if (hours === 0) return { key: 'onboarding.deadline.days', vars };
  return { key: 'onboarding.deadline.daysHours', vars };
}
