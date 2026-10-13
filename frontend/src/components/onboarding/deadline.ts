import { addWorkdays, formatDeadline, workdaysBetween } from '../../lib/workdays';

export { formatDeadline };

/**
 * The preview's onboarding deadline: 7 working days from now, recomputed on
 * every render so the countdown is real rather than a frozen screenshot.
 */
export function previewDeadlineLabel(): { date: Date; workdays: number } {
  const now = new Date();
  const date = addWorkdays(now, 7);
  return { date, workdays: workdaysBetween(now, date) };
}
