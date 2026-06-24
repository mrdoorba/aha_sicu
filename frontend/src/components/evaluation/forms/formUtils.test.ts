import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  parseCurrency,
  getCurrencyCode,
} from './formUtils';

describe('formatCurrency', () => {
  it('formats positive number with comma separators', () => {
    expect(formatCurrency(125000000)).toBe('125,000,000');
  });

  it('formats zero as "0"', () => {
    expect(formatCurrency(0)).toBe('0');
  });

  it('returns empty string for null', () => {
    expect(formatCurrency(null)).toBe('');
  });

  it('returns empty string for undefined', () => {
    expect(formatCurrency(undefined)).toBe('');
  });

  it('returns empty string for NaN', () => {
    expect(formatCurrency(NaN)).toBe('');
  });

  it('accepts marketplace param without changing output', () => {
    expect(formatCurrency(50000, 'TH')).toBe('50,000');
    expect(formatCurrency(50000, 'ID')).toBe('50,000');
  });
});

describe('parseCurrency', () => {
  it('parses comma-formatted string to number', () => {
    expect(parseCurrency('125,000,000')).toBe(125000000);
  });

  it('parses plain number string', () => {
    expect(parseCurrency('50000')).toBe(50000);
  });

  it('returns null for empty string', () => {
    expect(parseCurrency('')).toBeNull();
  });

  it('returns null for non-numeric string', () => {
    expect(parseCurrency('abc')).toBeNull();
  });

  it('returns null for whitespace-only string', () => {
    expect(parseCurrency('   ')).toBeNull();
  });

  it('accepts marketplace param without changing output', () => {
    expect(parseCurrency('1,000', 'TH')).toBe(1000);
    expect(parseCurrency('1,000', 'ID')).toBe(1000);
  });
});

describe('getCurrencyCode', () => {
  it('returns THB for TH marketplace', () => {
    expect(getCurrencyCode('TH')).toBe('THB');
  });

  it('returns IDR for ID marketplace', () => {
    expect(getCurrencyCode('ID')).toBe('IDR');
  });

  it('returns IDR when marketplace is undefined', () => {
    expect(getCurrencyCode()).toBe('IDR');
  });

  it('returns uppercased code for unknown marketplace', () => {
    expect(getCurrencyCode('XX')).toBe('XX');
  });

  it('handles lowercase marketplace input', () => {
    expect(getCurrencyCode('th')).toBe('THB');
    expect(getCurrencyCode('id')).toBe('IDR');
  });
});
