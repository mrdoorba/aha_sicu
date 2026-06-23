const INDONESIAN_MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
  'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des',
];

export function generatePeriodOptions(): string[] {
  const now = new Date();
  const options: string[] = [];
  for (let i = 0; i < 13; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    options.push(`${INDONESIAN_MONTHS[d.getMonth()]} ${d.getFullYear()}`);
  }
  return options;
}

/** Period label ("Mei 2026") for a "YYYY-MM" start month; current month if unset. */
export function periodLabelFromMonth(startMonth: string | null | undefined): string {
  if (!startMonth || !/^\d{4}-(0[1-9]|1[0-2])$/.test(startMonth)) {
    return generatePeriodOptions()[0];
  }
  const [year, month] = startMonth.split('-').map(Number);
  return `${INDONESIAN_MONTHS[month - 1]} ${year}`;
}
