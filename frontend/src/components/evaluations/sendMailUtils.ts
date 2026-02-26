const INDONESIAN_MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
  'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des',
];

export function formatPeriod(createdAt: string): string {
  const d = new Date(createdAt);
  return `${INDONESIAN_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

export function buildSubject(brandName: string, createdAt: string): string {
  return `\u{1F3E5} AHA Store Internal Check Up (Store ICU) - ${brandName} ${formatPeriod(createdAt)}`;
}

export function buildBody(
  picEmail: string,
  brandName: string,
  picName: string,
  storeLink: string,
  kategori: string,
  emailOutput: string,
): string {
  return `[EMAIL TO: ${picEmail}]

Kepada Pimpinan ${brandName} (Bapak/Ibu ${picName}) yang terhormat,

Berikut adalah *hasil AHA Store-Health Check-Up ${brandName} di Marketplace* [${storeLink}] dengan kategori ${kategori}

${emailOutput}`;
}
