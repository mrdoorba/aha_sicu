import { describe, it, expect } from 'vitest';
import { getIntlLocale } from './localeMap';

describe('getIntlLocale', () => {
  it('should return id-ID for id', () => {
    expect(getIntlLocale('id')).toBe('id-ID');
  });

  it('should return en-US for en', () => {
    expect(getIntlLocale('en')).toBe('en-US');
  });

  it('should return th-TH for th', () => {
    expect(getIntlLocale('th')).toBe('th-TH');
  });

  it('should return id-ID as fallback for unknown language', () => {
    expect(getIntlLocale('fr')).toBe('id-ID');
    expect(getIntlLocale('')).toBe('id-ID');
  });
});
