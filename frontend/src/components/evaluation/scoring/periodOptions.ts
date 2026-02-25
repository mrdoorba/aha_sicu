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
