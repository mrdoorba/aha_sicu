import { describe, expect, it } from 'vitest';
import {
  type NdaRecord,
  canCountersign,
  countersign,
  ndaWaitingOn,
  previewNdaQueue,
  signAsBrand,
} from './nda';

const blank: NdaRecord = {
  brandName: 'Test',
  pic: 'Someone',
  picRole: 'Direktur',
  status: 'awaiting_brand',
  brandRoute: null,
  brandSignedAt: null,
  ahaRoute: null,
  ahaSignedAt: null,
};

const now = new Date('2026-10-14T09:00:00Z');

describe('ndaWaitingOn', () => {
  it('names the side that still has to act', () => {
    expect(ndaWaitingOn('awaiting_brand')).toBe('brand');
    expect(ndaWaitingOn('awaiting_aha')).toBe('aha');
    expect(ndaWaitingOn('executed')).toBeNull();
  });
});

describe('canCountersign', () => {
  it('refuses a document the brand has not signed', () => {
    expect(canCountersign(blank)).toBe(false);
  });

  it('refuses an already-executed document', () => {
    const done = { ...blank, status: 'executed' as const, brandSignedAt: now };
    expect(canCountersign(done)).toBe(false);
  });

  it('allows it once the brand has signed', () => {
    expect(canCountersign(signAsBrand(blank, 'digital', now))).toBe(true);
  });
});

describe('signing', () => {
  it('moves the document to AHA after the brand signs', () => {
    const signed = signAsBrand(blank, 'paper', now);
    expect(signed.status).toBe('awaiting_aha');
    expect(signed.brandRoute).toBe('paper');
    expect(signed.brandSignedAt).toBe(now);
    expect(signed.ahaSignedAt).toBeNull();
  });

  it('executes once AHA counter-signs', () => {
    const done = countersign(signAsBrand(blank, 'digital', now), 'paper', now);
    expect(done.status).toBe('executed');
    expect(done.ahaRoute).toBe('paper');
    expect(ndaWaitingOn(done.status)).toBeNull();
  });

  it('lets each side pick its own route', () => {
    const done = countersign(signAsBrand(blank, 'paper', now), 'digital', now);
    expect(done.brandRoute).toBe('paper');
    expect(done.ahaRoute).toBe('digital');
  });

  it('cannot be counter-signed out of order', () => {
    // Skipping the brand's signature must leave the record untouched, not
    // produce an "executed" document only one party ever signed.
    const jumped = countersign(blank, 'digital', now);
    expect(jumped).toEqual(blank);
    expect(jumped.status).toBe('awaiting_brand');
  });

  it('never mutates the record it is given', () => {
    const before = { ...blank };
    signAsBrand(blank, 'digital', now);
    expect(blank).toEqual(before);
  });

  it('ignores a second brand signature', () => {
    const once = signAsBrand(blank, 'digital', now);
    expect(signAsBrand(once, 'paper', new Date())).toEqual(once);
  });
});

describe('previewNdaQueue', () => {
  it('covers every state the AHA signer will meet', () => {
    const statuses = previewNdaQueue().map((r) => r.status);
    expect(new Set(statuses)).toEqual(new Set(['awaiting_brand', 'awaiting_aha', 'executed']));
  });

  it('shows both routes as things the brand did', () => {
    const routes = previewNdaQueue().map((r) => r.brandRoute);
    expect(routes).toContain('digital');
    expect(routes).toContain('paper');
  });

  it('never has a signed timestamp without a route, or the reverse', () => {
    for (const r of previewNdaQueue()) {
      expect(r.brandRoute === null).toBe(r.brandSignedAt === null);
      expect(r.ahaRoute === null).toBe(r.ahaSignedAt === null);
    }
  });
});
