/**
 * The NDA's two-signature lifecycle.
 *
 * An NDA binds AHA Commerce, so AHA has to sign it too — a document carrying
 * only the brand's signature is not an agreement, it is a brand's unilateral
 * promise. Both sides can take either route independently: a partner who
 * insists on paper does not force AHA onto paper, and vice versa.
 */

export type NdaRoute = 'digital' | 'paper';

export type NdaStatus =
  /** Drafted, nobody has signed. */
  | 'awaiting_brand'
  /** The brand signed. AHA Commerce still has to counter-sign. */
  | 'awaiting_aha'
  /** Both parties have signed; this is the binding copy. */
  | 'executed';

export interface NdaRecord {
  brandName: string;
  /** Who signs for the brand. */
  pic: string;
  picRole: string;
  status: NdaStatus;
  /** How the brand signed. Null until they have. */
  brandRoute: NdaRoute | null;
  brandSignedAt: Date | null;
  /** How AHA counter-signed. Null until they have. */
  ahaRoute: NdaRoute | null;
  ahaSignedAt: Date | null;
}

/** Who the document is waiting on, and what that side should be told. */
export function ndaWaitingOn(status: NdaStatus): 'brand' | 'aha' | null {
  if (status === 'awaiting_brand') return 'brand';
  if (status === 'awaiting_aha') return 'aha';
  return null;
}

/**
 * Whether a record can move to `executed`.
 *
 * Deliberately not "did someone click the button": AHA cannot counter-sign a
 * document the brand has not signed, whichever route either side took. The
 * order is the whole point of a counter-signature.
 */
export function canCountersign(record: NdaRecord): boolean {
  return record.status === 'awaiting_aha' && record.brandSignedAt !== null;
}

/** Apply AHA's signature. Returns a new record; never mutates. */
export function countersign(record: NdaRecord, route: NdaRoute, at: Date): NdaRecord {
  if (!canCountersign(record)) return record;
  return { ...record, status: 'executed', ahaRoute: route, ahaSignedAt: at };
}

/** Apply the brand's signature. Returns a new record; never mutates. */
export function signAsBrand(record: NdaRecord, route: NdaRoute, at: Date): NdaRecord {
  if (record.status !== 'awaiting_brand') return record;
  return { ...record, status: 'awaiting_aha', brandRoute: route, brandSignedAt: at };
}

const hoursAgo = (h: number) => new Date(Date.now() - h * 3_600_000);

/**
 * The counter-signature queue, one row per state the AHA signer will meet.
 *
 * Both paper and digital appear as things the BRAND did, because that is the
 * variable the signer has to notice: a paper NDA means there is a scan to read
 * before signing, not just a form to confirm.
 */
export function previewNdaQueue(): NdaRecord[] {
  return [
    {
      brandName: 'Covermake',
      pic: 'Budi Santoso',
      picRole: 'Direktur Operasional',
      status: 'awaiting_aha',
      brandRoute: 'digital',
      brandSignedAt: hoursAgo(3),
      ahaRoute: null,
      ahaSignedAt: null,
    },
    {
      brandName: 'Lem Castol',
      pic: 'Rina Wijaya',
      picRole: 'Direktur Utama',
      status: 'awaiting_aha',
      brandRoute: 'paper',
      brandSignedAt: hoursAgo(26),
      ahaRoute: null,
      ahaSignedAt: null,
    },
    {
      brandName: 'Monkefit',
      pic: 'Andi Pratama',
      picRole: 'Founder',
      status: 'executed',
      brandRoute: 'paper',
      brandSignedAt: hoursAgo(72),
      ahaRoute: 'paper',
      ahaSignedAt: hoursAgo(48),
    },
    {
      brandName: 'คุณแม่จู้',
      pic: 'Somchai P.',
      picRole: 'Managing Director',
      status: 'awaiting_brand',
      brandRoute: null,
      brandSignedAt: null,
      ahaRoute: null,
      ahaSignedAt: null,
    },
  ];
}

/**
 * Who signs for AHA Commerce (Pihak Pertama).
 *
 * Marwah, 14 Oct: the first party's signatory is Pak Andre, not Partnership.
 * His full legal name and title still need confirming before this reaches a
 * real document — see docs/nda-requirements.md. Marwah still verifies manual
 * uploads; signing and verifying are deliberately different people.
 */
export const AHA_SIGNER = {
  name: 'Pak Andre',
  role: 'Penandatangan Pihak Pertama',
} as const;
