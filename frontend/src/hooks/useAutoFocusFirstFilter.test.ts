import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useAutoFocusFirstFilter } from './useAutoFocusFirstFilter';

/** Stand in for matchMedia, which jsdom does not implement. */
function mockViewport({ desktop }: { desktop: boolean }) {
  window.matchMedia = vi.fn().mockImplementation((query: string) => ({
    matches: desktop,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })) as unknown as typeof window.matchMedia;
}

describe('useAutoFocusFirstFilter', () => {
  let input: HTMLInputElement;

  beforeEach(() => {
    input = document.createElement('input');
    document.body.appendChild(input);
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  it('focuses the field on desktop', () => {
    mockViewport({ desktop: true });
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    result.current(input);

    expect(document.activeElement).toBe(input);
  });

  it('passes preventScroll so the page does not jump', () => {
    mockViewport({ desktop: true });
    const focus = vi.spyOn(input, 'focus');
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    result.current(input);

    expect(focus).toHaveBeenCalledWith({ preventScroll: true });
  });

  it('queries for width AND a fine pointer, not width alone', () => {
    mockViewport({ desktop: true });
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    result.current(input);

    expect(window.matchMedia).toHaveBeenCalledWith('(min-width: 1024px) and (pointer: fine)');
  });

  it('does nothing on touch devices', () => {
    mockViewport({ desktop: false });
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    result.current(input);

    expect(document.activeElement).not.toBe(input);
  });

  it('leaves focus alone when the user already focused something', () => {
    mockViewport({ desktop: true });
    const other = document.createElement('button');
    document.body.appendChild(other);
    other.focus();

    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());
    result.current(input);

    expect(document.activeElement).toBe(other);
  });

  it('fires once, so a re-attached node does not steal focus back', () => {
    mockViewport({ desktop: true });
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    result.current(input);
    const other = document.createElement('button');
    document.body.appendChild(other);
    other.focus();

    // Node re-attaches on a later render — must not yank focus from the user.
    result.current(input);

    expect(document.activeElement).toBe(other);
  });

  it('tolerates a null node, as happens while a list page shows its skeleton', () => {
    mockViewport({ desktop: true });
    const { result } = renderHook(() => useAutoFocusFirstFilter<HTMLInputElement>());

    expect(() => result.current(null)).not.toThrow();

    // ...and still focuses once the real node arrives.
    result.current(input);
    expect(document.activeElement).toBe(input);
  });
});
