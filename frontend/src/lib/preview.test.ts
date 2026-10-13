import { describe, it, expect } from 'vitest';
import { isPreviewEnabled } from './preview';

describe('isPreviewEnabled', () => {
  it('allows local development hosts', () => {
    expect(isPreviewEnabled('localhost')).toBe(true);
    expect(isPreviewEnabled('127.0.0.1')).toBe(true);
  });

  it('allows the Firebase dev target', () => {
    expect(isPreviewEnabled('aha-coms-sicu-dev.web.app')).toBe(true);
    expect(isPreviewEnabled('aha-coms-sicu-dev.firebaseapp.com')).toBe(true);
  });

  it('REFUSES production', () => {
    expect(isPreviewEnabled('aha-coms-sicu-prod.web.app')).toBe(false);
    expect(isPreviewEnabled('sicu.ahabot.ai')).toBe(false);
  });

  it('fails closed on an unrecognised host', () => {
    expect(isPreviewEnabled('example.com')).toBe(false);
    expect(isPreviewEnabled('')).toBe(false);
  });

  it('is not fooled by a lookalike domain', () => {
    // Both of these would pass a prefix/substring test. Anyone can register
    // the second one, so the allowlist matches whole hosts.
    expect(isPreviewEnabled('evil-aha-coms-sicu-dev.web.app')).toBe(false);
    expect(isPreviewEnabled('aha-coms-sicu-dev.attacker.com')).toBe(false);
  });

  it('ignores host casing', () => {
    expect(isPreviewEnabled('AHA-COMS-SICU-DEV.web.app')).toBe(true);
  });
});
