import i18n from '../../i18n';

export function buildSubject(brandName: string, period: string): string {
  return i18n.t('sendMailUtils.subject', { brandName, period });
}

export function buildBody(
  picEmail: string,
  brandName: string,
  picName: string,
  storeLink: string,
  kategori: string,
  emailOutput: string,
): string {
  const salutation = i18n.t('sendMailUtils.salutation', { brandName, picName });
  const intro = i18n.t('sendMailUtils.intro', { brandName, storeLink, kategori });

  return `[EMAIL TO: ${picEmail}]

${salutation}

${intro}

${emailOutput}`;
}
