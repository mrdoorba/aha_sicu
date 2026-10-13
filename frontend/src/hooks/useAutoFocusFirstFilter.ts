import { useCallback, useRef } from 'react';

/**
 * Desktop means a wide viewport AND a precise pointer. Width alone would catch
 * a tablet in landscape, where focusing a field summons the on-screen keyboard
 * over the content the user came to read.
 */
const DESKTOP_QUERY = '(min-width: 1024px) and (pointer: fine)';

/**
 * Focus a report/dashboard/list page's first filter field once it mounts.
 *
 * Returns a ref callback — attach it to the field itself:
 *
 *     const autoFocusRef = useAutoFocusFirstFilter<HTMLInputElement>();
 *     <Input ref={autoFocusRef} ... />
 *
 * A ref callback rather than a RefObject because list pages render a skeleton
 * first: an effect keyed to mount would run while the field is still null and
 * never fire again. This fires exactly when the node attaches, however late.
 *
 * The field is focused, never opened. `.focus()` on an input or a select
 * trigger moves the caret without popping a dropdown — the user can type
 * immediately, but the page still looks at rest.
 *
 * Skipped entirely when something is already focused, so a user who clicks
 * faster than the data loads keeps their target.
 */
export function useAutoFocusFirstFilter<T extends HTMLElement>(): (el: T | null) => void {
  const alreadyFocused = useRef(false);

  return useCallback((el: T | null) => {
    if (!el || alreadyFocused.current) return;
    if (!window.matchMedia?.(DESKTOP_QUERY).matches) return;

    // document.body is what the browser reports when nothing is focused;
    // anything else means the user got there first.
    const active = document.activeElement;
    if (active && active !== document.body && active !== document.documentElement) return;

    alreadyFocused.current = true;
    el.focus({ preventScroll: true });
  }, []);
}
