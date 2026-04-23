import type { TFunction } from 'i18next';
import i18n from '../../i18n';

export function buildSubject(brandName: string, period: string, t?: TFunction): string {
  const translate = t ?? i18n.t;
  return translate('sendMailUtils.subject', { brandName, period });
}

export function buildBody(
  picEmail: string,
  brandName: string,
  picName: string,
  storeLink: string,
  kategori: string,
  emailOutput: string,
  t?: TFunction,
  emailBodyOverride?: string,
): string {
  const translate = t ?? i18n.t;
  const salutation = translate('sendMailUtils.salutation', { brandName, picName });
  const intro = translate('sendMailUtils.intro', { brandName, storeLink, kategori });
  const bodyContent = emailBodyOverride ?? emailOutput;

  return `[EMAIL TO: ${picEmail}]

${salutation}

${intro}

${bodyContent}`;
}

export function buildMailtoUrl(to: string, subject: string, body: string): string {
  const params = new URLSearchParams({
    subject,
    body,
  });

  return `mailto:${encodeURIComponent(to)}?${params.toString()}`;
}

export function openMailto(url: string): void {
  window.open(url, '_self');
}
