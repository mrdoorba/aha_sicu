import { describe, it, expect } from 'vitest';
import { lookupVoucher, PREVIEW_TEST_CODES, VOUCHER_CODE_LENGTH } from './onboarding';

describe('lookupVoucher', () => {
  it('stays neutral on an empty field', () => {
    expect(lookupVoucher('').state).toBe('idle');
    expect(lookupVoucher('   ').state).toBe('idle');
  });

  it('does not judge a half-typed code', () => {
    // Shouting "not found" at someone four characters in is the bug this guards.
    const result = lookupVoucher('K7M4');
    expect(result.state).toBe('typing');
    if (result.state === 'typing') {
      expect(result.remaining).toBe(VOUCHER_CODE_LENGTH - 4);
    }
  });

  it('accepts the valid code', () => {
    const result = lookupVoucher(PREVIEW_TEST_CODES.valid);
    expect(result.state).toBe('valid');
    if (result.state === 'valid') {
      expect(result.brand.name).toBe('Covermake');
      expect(result.expiresAt.getTime()).toBeGreaterThan(Date.now());
    }
  });

  it('is case- and whitespace-insensitive', () => {
    expect(lookupVoucher(`  ${PREVIEW_TEST_CODES.valid.toLowerCase()}  `).state).toBe('valid');
  });

  it('separates expired from unknown', () => {
    const expired = lookupVoucher(PREVIEW_TEST_CODES.expired);
    expect(expired.state).toBe('expired');
    if (expired.state === 'expired') {
      expect(expired.expiredOn.getTime()).toBeLessThan(Date.now());
    }
  });

  it('separates already-claimed from unknown', () => {
    expect(lookupVoucher(PREVIEW_TEST_CODES.claimed).state).toBe('claimed');
  });

  it('reports an unrecognised full-length code as unknown', () => {
    expect(lookupVoucher('ZZZZZZZZZZZZ').state).toBe('unknown');
  });

  it('never returns valid for anything but the issued code', () => {
    for (const candidate of ['', 'K7M4PXQ9TRJ', 'K7M4PXQ9TRJ3', 'ZZZZZZZZZZZZ']) {
      expect(lookupVoucher(candidate).state).not.toBe('valid');
    }
  });
});
