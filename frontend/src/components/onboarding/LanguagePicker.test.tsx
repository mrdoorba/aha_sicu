import { describe, expect, it, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import i18n from '../../i18n';
import { ONBOARDING_LANG_KEY, readOnboardingLanguage } from '../../lib/onboardingLanguage';
import { LanguagePicker } from './LanguagePicker';

describe('LanguagePicker', () => {
  beforeEach(async () => {
    localStorage.clear();
    await i18n.changeLanguage('id');
  });

  it('switches the flow’s language and remembers the choice', async () => {
    render(<LanguagePicker />);
    await userEvent.click(screen.getByRole('button', { name: /EN/ }));

    expect(i18n.language).toBe('en');
    // A brand who picks a language on the claim page and reloads on step 4 has
    // no account yet, so localStorage is the only place to keep it.
    expect(localStorage.getItem(ONBOARDING_LANG_KEY)).toBe('en');
  });

  it('marks only the active language as pressed', async () => {
    render(<LanguagePicker />);
    await userEvent.click(screen.getByRole('button', { name: /TH/ }));

    const pressed = screen
      .getAllByRole('button')
      .filter((b) => b.getAttribute('aria-pressed') === 'true');
    expect(pressed).toHaveLength(1);
    expect(pressed[0]).toHaveTextContent('TH');
  });

  it('still switches when storage is blocked', async () => {
    // Private browsing throws on setItem. Losing the memory is acceptable;
    // refusing to change language because of it would not be.
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked');
    });
    render(<LanguagePicker />);
    await userEvent.click(screen.getByRole('button', { name: /EN/ }));

    expect(i18n.language).toBe('en');
    vi.restoreAllMocks();
  });
});

describe('readOnboardingLanguage', () => {
  beforeEach(() => localStorage.clear());

  it('ignores a value that is not one of our languages', () => {
    localStorage.setItem(ONBOARDING_LANG_KEY, 'fr');
    expect(readOnboardingLanguage()).toBeNull();
  });

  it('returns nothing when the key was never written', () => {
    expect(readOnboardingLanguage()).toBeNull();
  });

  it('returns a language we actually ship', () => {
    localStorage.setItem(ONBOARDING_LANG_KEY, 'th');
    expect(readOnboardingLanguage()).toBe('th');
  });
});
