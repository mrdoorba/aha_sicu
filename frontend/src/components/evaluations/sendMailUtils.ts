import type { TFunction } from 'i18next';
import i18n from '../../i18n';

const GMAIL_COMPOSE_BASE_URL = 'https://mail.google.com/mail/';
// Thai payloads expand substantially after URL encoding. When the compose URL
// gets large, opening a blank tab first and then assigning location is safer
// than passing the full URL into window.open() directly.
const GMAIL_STAGED_OPEN_URL_LENGTH_THRESHOLD = 700;

export interface GmailComposeLink {
  strategy: 'direct' | 'staged';
  url: string;
}

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


export function buildGmailComposeUrl(to: string, subject: string, body: string): string {
  const params = new URLSearchParams({
    view: 'cm',
    fs: '1',
    to,
    su: subject,
    body,
  });

  return `${GMAIL_COMPOSE_BASE_URL}?${params.toString()}`;
}

export function buildGmailComposeLink(
  to: string,
  subject: string,
  body: string,
): GmailComposeLink {
  const url = buildGmailComposeUrl(to, subject, body);

  return {
    strategy: url.length > GMAIL_STAGED_OPEN_URL_LENGTH_THRESHOLD ? 'staged' : 'direct',
    url,
  };
}

export function openGmailCompose(link: GmailComposeLink): void {
  if (link.strategy === 'staged') {
    const composeWindow = window.open('', '_blank');
    if (composeWindow) {
      composeWindow.opener = null;
      composeWindow.location.replace(link.url);
      return;
    }
  }

  window.open(link.url, '_blank', 'noopener,noreferrer');
}
