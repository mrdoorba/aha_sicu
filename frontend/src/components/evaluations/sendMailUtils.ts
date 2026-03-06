export function buildSubject(brandName: string, period: string): string {
  return `\u{1F3E5} AHA Store Internal Check Up (Store ICU) - ${brandName} ${period}`;
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
