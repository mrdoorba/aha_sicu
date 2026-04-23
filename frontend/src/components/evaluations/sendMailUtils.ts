import type { TFunction } from 'i18next';
import i18n from '../../i18n';

const GMAIL_COMPOSE_BASE_URL = 'https://mail.google.com/mail/';
// Thai copy expands much more aggressively once URL-encoded than the current
// EN/ID payloads. Past this point, Gmail can blank/400 on query-string compose,
// so we switch to a form POST handoff instead.
const GMAIL_GET_URL_LENGTH_THRESHOLD = 700;

type GmailComposeParams = Record<'view' | 'fs' | 'to' | 'su' | 'body', string>;

export interface GmailComposeRequest {
  method: 'get' | 'post';
  url: string;
  params: GmailComposeParams;
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

function buildGmailComposeParams(to: string, subject: string, body: string): GmailComposeParams {
  return {
    view: 'cm',
    fs: '1',
    to,
    su: subject,
    body,
  };
}

export function buildGmailComposeUrl(to: string, subject: string, body: string): string {
  const params = new URLSearchParams(buildGmailComposeParams(to, subject, body));

  return `${GMAIL_COMPOSE_BASE_URL}?${params.toString()}`;
}

export function buildGmailComposeRequest(
  to: string,
  subject: string,
  body: string,
): GmailComposeRequest {
  const params = buildGmailComposeParams(to, subject, body);
  const url = buildGmailComposeUrl(to, subject, body);

  return {
    method: url.length > GMAIL_GET_URL_LENGTH_THRESHOLD ? 'post' : 'get',
    url,
    params,
  };
}

export function openGmailCompose(request: GmailComposeRequest): void {
  if (request.method === 'get') {
    window.open(request.url, '_blank', 'noopener,noreferrer');
    return;
  }

  const form = document.createElement('form');
  form.action = GMAIL_COMPOSE_BASE_URL;
  form.method = 'post';
  form.target = '_blank';
  form.style.display = 'none';

  for (const [name, value] of Object.entries(request.params)) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    form.appendChild(input);
  }

  document.body.appendChild(form);
  try {
    form.submit();
  } finally {
    form.remove();
  }
}
